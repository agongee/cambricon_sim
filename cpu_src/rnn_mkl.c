#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include <mkl.h>

#define LOOP 10

void initializer(float* arr, int size, int bias){
    int i;
    for(i = 0; i < size; i++){
        arr[i] = (float)(i+bias);
    }
}

uint64_t rdtsc(){
    uint64_t lo,hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((uint64_t)hi << 32) | lo;
}


int main(){
    float *in, *ht, *h1, *out;
    float *w_hh, *w_xh, *w_hy;
    float *bh, *by;
    int in_dim, h_dim, out_dim;
    int i;
    double s_initial, s_elapsed;
    uint64_t c_initial, c_elapsed, c_t_initial, c_t_elapsed;

    c_t_initial = rdtsc();

    in_dim = 26;
    h_dim = 93;
    out_dim = 61;

    in = (float *)mkl_malloc(in_dim*sizeof(float), 32);
    ht = (float *)mkl_malloc(h_dim*sizeof(float), 32);
    h1 = (float *)mkl_malloc(h_dim*sizeof(float), 32);
    out = (float *)mkl_malloc(out_dim*sizeof(float), 32);

    w_hh = (float *)mkl_malloc(h_dim*h_dim*sizeof(float), 32);
    w_xh = (float *)mkl_malloc(in_dim*h_dim*sizeof(float), 32);
    w_hy = (float *)mkl_malloc(h_dim*out_dim*sizeof(float), 32);

    bh = (float *)mkl_malloc(h_dim*sizeof(float), 32);
    by = (float *)mkl_malloc(out_dim*sizeof(float), 32);

    printf(" Initializing Input and Weight Data\n\n");
    s_initial = dsecnd();
    c_initial = rdtsc();
    initializer(in, in_dim, 1);
    initializer(w_hh, h_dim*h_dim, 2);
    initializer(w_xh, in_dim*h_dim, 3);
    initializer(w_hy, h_dim*out_dim, 4);
    initializer(bh, h_dim, 5);
    initializer(by, out_dim, 6);
    c_elapsed = rdtsc() - c_initial;
    s_elapsed = dsecnd() - s_initial;
    printf (" == Data initialization using Intel(R) MKL completed == \n"
            " == at %.5f milliseconds and %llu cycles== \n\n", (s_elapsed * 1000), c_elapsed);

    printf(" RNN Computation\n\n");
    s_initial = dsecnd();
    c_initial = rdtsc();
    for(i = 0; i < LOOP; i++){
        // w_xh * x
        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    1, h_dim, in_dim, 1, in, in_dim, w_xh, h_dim, 0, ht, h_dim);
        
        // w_hh * h
        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    1, h_dim, h_dim, 1, h1, h_dim, w_hh, h_dim, 0, h1, h_dim);

        vsAdd(h_dim, h1, ht, h1);
        vsAdd(h_dim, h1, bh, h1);

        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    1, out_dim, h_dim, 1, h1, h_dim, w_hy, out_dim, 0, out, out_dim);
        
        initializer(in, in_dim, i); // pseudo-input
    }
    c_elapsed = (rdtsc() - c_initial) / LOOP;
    s_elapsed = (dsecnd() - s_initial) / LOOP;

    printf (" == RNN computation using Intel(R) MKL completed == \n"
            " == at %.5f milliseconds and %llu cycles == \n\n", (s_elapsed * 1000), c_elapsed);
    
    printf (" Deallocating memory \n\n");

    mkl_free(in);
    mkl_free(ht);
    mkl_free(h1);
    mkl_free(out);
    mkl_free(w_hh);
    mkl_free(w_xh);
    mkl_free(w_hy);
    mkl_free(bh);
    mkl_free(by);

    c_t_elapsed = rdtsc() - c_t_initial;

    printf (" RNN Benchmark completed in %llu cycles.\n\n", c_t_elapsed);
    return 0;

}