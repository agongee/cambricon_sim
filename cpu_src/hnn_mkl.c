#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include <mkl.h>

#define LOOP 10

uint64_t rdtsc(){
    uint64_t lo,hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((uint64_t)hi << 32) | lo;
}

// vector(5) - components(100)

int main(){

    int v_num, v_comp;
    float *vects, *vect_temp, *in; // input
    float *weight, *weight_temp, *weight_thresh_temp, *thresh; // weight
    float *identity; // I
    float *computation_temp, *u, *b, *b_temp;
    float *neg_half;
    float thresh_temp;
    int i, j, loop;

    v_num = 5;
    v_comp = 100;

    neg_half = (float *)mkl_malloc(v_comp*sizeof(float), 32);
    for(i = 0; i < v_comp; i++){
        neg_half[i] = -0.5;
    }

    vects = (float *)mkl_calloc(v_num*v_comp, sizeof(float), 32);
    in = (float *)mkl_malloc(v_comp*sizeof(float), 32);
    weight = (float *)mkl_malloc(v_comp*v_comp*sizeof(float), 32);
    weight_temp = (float *)mkl_malloc(v_comp*v_comp*sizeof(float), 32);
    thresh = (float *)mkl_malloc(v_comp*sizeof(float), 32);
    identity = (float *)mkl_malloc(v_comp*v_comp*sizeof(float), 32);
    computation_temp = (float *)mkl_malloc(v_comp*sizeof(float), 32);
    u = (float *)mkl_malloc(v_comp*sizeof(float), 32);
    b = (float *)mkl_malloc(v_comp*sizeof(float), 32);
    b_temp = (float *)mkl_malloc(v_comp*sizeof(float), 32);
    double s_initial, s_elapsed;
    uint64_t c_initial, c_elapsed, c_t_initial, c_t_elapsed;

    char enter = 0;

    printf(" HNN CPU Benchmark Computation!\n");
    printf(" CPU Allocation must be Processed!\n");
    printf(" Press Enter to Continue!\n");
    while (enter != '\r' && enter != '\n') { enter = getchar(); }

    c_t_initial = rdtsc();

    printf(" Initializing Input and Weight Data\n\n");
    s_initial = dsecnd();
    c_initial = rdtsc();
    for(i = 0; i < v_num*v_comp; i++){
        vects[i] = (rand() % 2 == 0) ? 1 : -1;
    }

    for(i = 0; i < v_comp; i++){
        identity[i*v_comp+i] = (-1) * v_num;
        in[i], b_temp[i], b[i] = rand() % 2 == 0;
    }
    c_elapsed = rdtsc() - c_initial;
    s_elapsed = dsecnd() - s_initial;
    printf (" == Data initialization using Intel(R) MKL completed == \n"
            " == at %.5f milliseconds and %llu cycles== \n\n", (s_elapsed * 1000), c_elapsed);

    printf(" HNN Training\n\n");
    s_initial = dsecnd();
    c_initial = rdtsc();
    for(loop = 0; loop < LOOP; loop++){
        vect_temp = vects;

        for(i = 0; i < v_num; i++){
            if(i == 0){
                cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    v_comp, v_comp, 1, 1, vect_temp, 1, vect_temp, v_comp, 1, weight, v_comp);
            }
            else{
                cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    v_comp, v_comp, 1, 1, vect_temp, 1, vect_temp, v_comp, 1, weight_temp, v_comp);
                vsAdd(v_comp*v_comp, weight, weight_temp, weight);
            }
            vect_temp += v_comp;
        }

        vsAdd(v_comp*v_comp, weight, identity, weight);
                
    }
    c_elapsed = (rdtsc() - c_initial) / LOOP;
    s_elapsed = (dsecnd() - s_initial) / LOOP;

    printf (" == HNN Training using Intel(R) MKL completed == \n"
            " == at %.5f milliseconds and %llu cycles == \n\n", (s_elapsed * 1000), c_elapsed);

    printf(" HNN Inference\n\n");
    s_initial = dsecnd();
    c_initial = rdtsc();
    for(loop = 0; loop < LOOP; loop++){

        weight_thresh_temp = weight;

        for(i = 0; i < v_comp; i++){
            vsAdd(v_comp, thresh, weight_thresh_temp, thresh);
            weight_thresh_temp += v_comp;
        }
        vsMul(v_comp, thresh, thresh, neg_half);

        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                v_comp, 1, v_comp, 1, weight, v_comp, in, 1, 1, u, 1);
        
        vsAdd(v_comp, u, thresh, u);
        
        for(i = 0; i < v_comp; i++){
            if(u[i] > 0){
                b_temp[i] = 1;
            }
            else if(u[i] < 0){
                b_temp[i] = 0;
            }
            else{
                b_temp[i] = b[i];
            }
        }

        memcpy(b, b_temp, sizeof(float)*v_comp);
        
    }
    c_elapsed = (rdtsc() - c_initial) / LOOP;
    s_elapsed = (dsecnd() - s_initial) / LOOP;
    printf (" == HNN Inference using Intel(R) MKL completed == \n"
            " == at %.5f milliseconds and %llu cycles == \n\n", (s_elapsed * 1000), c_elapsed);
    
    printf (" Deallocating memory \n\n");

    mkl_free(vects);
    mkl_free(in);
    mkl_free(weight);
    mkl_free(weight_temp);
    mkl_free(thresh);
    mkl_free(identity);
    mkl_free(computation_temp);
    mkl_free(u);

    c_t_elapsed = rdtsc() - c_t_initial;

    printf (" MLP Benchmark completed in %llu cycles.\n\n", c_t_elapsed);
    return 0;
}