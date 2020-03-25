#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#include <mkl.h>

#define LOOP 10

uint64_t rdtsc(){
    uint64_t lo,hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((uint64_t)hi << 32) | lo;
}

// in(64) - h1(150) - h2(150) - out(14)

int main(){
    float *in, *temp; // input
    float *weight, *temp_weight, *to_update_weight; // weight
    float *update;
    int in_dim, w_dim;
    int min_dist;
    int loop, i, temp_dist, dist;
    double s_initial, s_elapsed;
    uint64_t c_initial, c_elapsed, c_t_initial, c_t_elapsed;

    c_t_initial = rdtsc();

    in_dim = 64;
    w_dim = 36;

    in = (float *)mkl_malloc(in_dim*sizeof(float), 32);
    temp = (float *)mkl_malloc(in_dim*sizeof(float), 32);
    weight = (float *)mkl_malloc(in_dim*w_dim*sizeof(float), 32);
    update = (float *)mkl_malloc(in_dim*sizeof(float), 32);

    printf(" Initializing Input and Weight Data\n\n");
    s_initial = dsecnd();
    c_initial = rdtsc();
    for(i = 0; i < in_dim; i++){
        in[i] = (float)(i+1);
        update[i] = 0.4;
    }

    for(i = 0; i < in_dim*w_dim; i++){
        weight[i] = (float)(i+1);
    }
    c_elapsed = rdtsc() - c_initial;
    s_elapsed = dsecnd() - s_initial;
    printf (" == Data initialization using Intel(R) MKL completed == \n"
            " == at %.5f milliseconds and %llu cycles== \n\n", (s_elapsed * 1000), c_elapsed);

    if(in == NULL || weight == NULL){
        printf( "\n ERROR: Can't allocate memory for matrices. Aborting... \n\n");
        mkl_free(in);
        mkl_free(weight);
        return 1;
    }
    dist = 1 << 15;
    printf(" SOM Computation\n\n");
    s_initial = dsecnd();
    c_initial = rdtsc();
    for(loop = 0; loop < LOOP; loop++){

        temp_weight = weight;
        
        for(i = 0; i < w_dim; i++){
            vsSub(in_dim, in, temp_weight, temp);
            temp_dist = cblas_snrm2(in_dim, temp, 1);
            if(dist > temp_dist){
                dist = temp_dist;
                to_update_weight = temp_weight;
            }
            temp_weight += in_dim;
        }
        
        vsMul(in_dim, to_update_weight, update, to_update_weight);
        
    }
    c_elapsed = (rdtsc() - c_initial) / LOOP;
    s_elapsed = (dsecnd() - s_initial) / LOOP;

    printf (" == SOM computation using Intel(R) MKL completed == \n"
            " == at %.5f milliseconds and %llu cycles == \n\n", (s_elapsed * 1000), c_elapsed);
    
    printf (" Deallocating memory \n\n");
    mkl_free(in);
    mkl_free(temp);
    mkl_free(weight);
    mkl_free(update);

    c_t_elapsed = rdtsc() - c_t_initial;

    printf (" MLP Benchmark completed in %llu cycles.\n\n", c_t_elapsed);
    return 0;
}