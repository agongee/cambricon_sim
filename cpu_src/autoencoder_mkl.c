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

// in(64) - h1(150) - h2(150) - out(14)
// input(320) - H1(200) - H2(100) - H3(50) - Output(10)

int main(){
    float *in, *h1, *h2, *h3, *out; // activations
    float *h1_exp, *h2_exp, *h3_exp, *out_exp; // exponentioal, sigmoid
    float *in_h1, *h1_h2, *h2_h3, *h3_out; // weights
    float *one; // vector of one
    int in_dim, h1_dim, h2_dim, h3_dim, out_dim; // dimensions
    int loop, i, k;
    double s_initial, s_elapsed;
    uint64_t c_initial, c_elapsed, c_t_initial, c_t_elapsed;

    c_t_initial = rdtsc();

    in_dim = 320;
    h1_dim = 200;
    h2_dim = 100;
    h3_dim = 50;
    out_dim = 10;
    k = 1;

    one = (float *)mkl_malloc(h1_dim*sizeof(float), 32);

    in = (float *)mkl_malloc(in_dim*sizeof(float), 32);
    h1 = (float *)mkl_malloc(h1_dim*sizeof(float), 32);
    h2 = (float *)mkl_malloc(h2_dim*sizeof(float), 32);
    h3 = (float *)mkl_malloc(h3_dim*sizeof(float), 32);
    out = (float *)mkl_malloc(out_dim*sizeof(float), 32);

    in_h1 = (float *)mkl_malloc(in_dim*h1_dim*sizeof(float), 32);
    h1_h2 = (float *)mkl_malloc(h1_dim*h2_dim*sizeof(float), 32);
    h2_h3 = (float *)mkl_malloc(h2_dim*h3_dim*sizeof(float), 32);
    h3_out = (float *)mkl_malloc(h3_dim*out_dim*sizeof(float), 32);

    h1_exp = (float *)mkl_malloc(h1_dim*sizeof(float), 32);
    h2_exp = (float *)mkl_malloc(h2_dim*sizeof(float), 32);
    h3_exp = (float *)mkl_malloc(h3_dim*sizeof(float), 32);
    out_exp = (float *)mkl_malloc(out_dim*sizeof(float), 32);


    printf(" Initializing Input and Weight Data\n\n");
    s_initial = dsecnd();
    c_initial = rdtsc();
    for(i = 0; i < in_dim; i++){
        in[i] = (float)(i+1);
    }

    for(i = 0; i < in_dim*h1_dim; i++){
        in_h1[i] = (float)(i+2);
    }

    for(i = 0; i < h1_dim*h2_dim; i++){
        h1_h2[i] = (float)(i+3);
    }

    for(i = 0; i < h2_dim*h3_dim; i++){
        h2_h3[i] = (float)(i+4);
    }

    for(i = 0; i < h3_dim*out_dim; i++){
        h3_out[i] = (float)(i+5);
    }

    c_elapsed = rdtsc() - c_initial;
    s_elapsed = dsecnd() - s_initial;
    printf (" == Data initialization using Intel(R) MKL completed == \n"
            " == at %.5f milliseconds and %llu cycles== \n\n", (s_elapsed * 1000), c_elapsed);

    if(in == NULL || in_h1 == NULL || h1_h2 == NULL || h2_h3 == NULL || h3_out == NULL 
            || h1 == NULL || h2 == NULL || h3 == NULL || out == NULL || h1_exp == NULL 
            || h2_exp == NULL || h3_exp == NULL || out_exp == NULL){
        printf( "\n ERROR: Can't allocate memory for matrices. Aborting... \n\n");
        mkl_free(in);
        mkl_free(in_h1);
        mkl_free(h1_h2);
        mkl_free(h2_h3);
        mkl_free(h3_out);
        mkl_free(h1);
        mkl_free(h2);
        mkl_free(h3);
        mkl_free(out);
        mkl_free(h1_exp);
        mkl_free(h2_exp);
        mkl_free(h3_exp);
        mkl_free(out_exp);
        return 1;
    }

    printf(" MLP Computation\n\n");
    s_initial = dsecnd();
    c_initial = rdtsc();
    for(loop = 0; loop < LOOP; loop++){
        // in - h1
        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    1, h1_dim, in_dim, 1, in, in_dim, in_h1, h1_dim, 1, h1, h1_dim);
        vsExp(h1_dim, h1, h1_exp);
        vsAdd(h1_dim, h1_exp, one, h1);
        vsDiv(h1_dim, h1, h1_exp, h1);
        
        // h1 - h2
        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    1, h2_dim, h1_dim, 1, h1, h1_dim, h1_h2, h2_dim, 1, h2, h2_dim);
        vsExp(h2_dim, h2, h2_exp);
        vsAdd(h2_dim, h2_exp, one, h2);
        vsDiv(h2_dim, h2, h2_exp, h2);

        // h2 - h3
        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    1, h3_dim, h2_dim, 1, h2, h2_dim, h2_h3, h3_dim, 1, h3, h3_dim);
        vsExp(h3_dim, h3, h3_exp);
        vsAdd(h3_dim, h3_exp, one, h3);
        vsDiv(h3_dim, h3, h3_exp, h3);

        // h3 - out
        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    1, out_dim, h3_dim, 1, h3, h3_dim, h3_out, out_dim, 1, out, out_dim);
        vsExp(out_dim, out, out_exp);
        vsAdd(out_dim, out_exp, one, out);
        vsDiv(out_dim, out, out_exp, out);

    }
    c_elapsed = (rdtsc() - c_initial) / LOOP;
    s_elapsed = (dsecnd() - s_initial) / LOOP;

    printf (" == MLP computation using Intel(R) MKL completed == \n"
            " == at %.5f milliseconds and %llu cycles == \n\n", (s_elapsed * 1000), c_elapsed);
    
    printf (" Deallocating memory \n\n");
    mkl_free(in);
    mkl_free(in_h1);
    mkl_free(h1_h2);
    mkl_free(h2_h3);
    mkl_free(h3_out);
    mkl_free(h1);
    mkl_free(h2);
    mkl_free(h3);
    mkl_free(out);
    mkl_free(h1_exp);
    mkl_free(h2_exp);
    mkl_free(h3_exp);
    mkl_free(out_exp);

    c_t_elapsed = rdtsc() - c_t_initial;

    printf (" MLP Benchmark completed in %llu cycles.\n\n", c_t_elapsed);
    return 0;
}