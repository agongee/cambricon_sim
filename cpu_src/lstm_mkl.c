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
    float *x, *h, *f, *i, *o, *g, *c;
    float *w_xhf, *w_hhf, *w_xhi, *w_hhi, *w_xho, *w_hho, *w_xhg, *w_hhg;
    float *b_hf, *b_hi, *b_ho, *b_hg;
    float *f_exp, *i_exp, *o_exp;
    float *temp;
    int in_dim, h_dim;
    int loop, j;
    double s_initial, s_elapsed;
    uint64_t c_initial, c_elapsed, c_t_initial, c_t_elapsed;

    c_t_initial = rdtsc();
    in_dim = 26;
    h_dim = 93;

    x = (float *)mkl_malloc(in_dim*sizeof(float), 32);
    h = (float *)mkl_malloc(h_dim*sizeof(float), 32);
    f = (float *)mkl_malloc(h_dim*sizeof(float), 32);
    i = (float *)mkl_malloc(h_dim*sizeof(float), 32);
    o = (float *)mkl_malloc(h_dim*sizeof(float), 32);
    g = (float *)mkl_malloc(h_dim*sizeof(float), 32);
    c = (float *)mkl_malloc(h_dim*sizeof(float), 32);

    w_xhf = (float *)mkl_malloc(in_dim*h_dim*sizeof(float), 32);
    w_hhf = (float *)mkl_malloc(h_dim*h_dim*sizeof(float), 32);
    w_xhi = (float *)mkl_malloc(in_dim*h_dim*sizeof(float), 32);
    w_hhi = (float *)mkl_malloc(h_dim*h_dim*sizeof(float), 32);
    w_xho = (float *)mkl_malloc(in_dim*h_dim*sizeof(float), 32);
    w_hho = (float *)mkl_malloc(h_dim*h_dim*sizeof(float), 32);
    w_xhg = (float *)mkl_malloc(in_dim*h_dim*sizeof(float), 32);
    w_hhg = (float *)mkl_malloc(h_dim*h_dim*sizeof(float), 32);

    f_exp = (float *)mkl_malloc(h_dim*sizeof(float), 32);
    i_exp = (float *)mkl_malloc(h_dim*sizeof(float), 32);
    o_exp = (float *)mkl_malloc(h_dim*sizeof(float), 32);

    temp = (float *)mkl_malloc(h_dim*sizeof(float), 32);

    b_hf = (float *)mkl_malloc(h_dim*sizeof(float), 32);
    b_hi = (float *)mkl_malloc(h_dim*sizeof(float), 32);
    b_ho = (float *)mkl_malloc(h_dim*sizeof(float), 32);
    b_hg = (float *)mkl_malloc(h_dim*sizeof(float), 32);

    printf(" Initializing Input and Weight Data\n\n");
    s_initial = dsecnd();
    c_initial = rdtsc();
    initializer(x, in_dim, 1);
    initializer(h, h_dim, 2);
    initializer(c, h_dim, 3);
    initializer(w_hhf, h_dim*h_dim, 4);
    initializer(w_xhf, in_dim*h_dim, 5);
    initializer(w_hhi, h_dim*h_dim, 6);
    initializer(w_xhi, in_dim*h_dim, 7);
    initializer(w_hho, h_dim*h_dim, 8);
    initializer(w_xho, in_dim*h_dim, 9);
    initializer(w_hhg, h_dim*h_dim, 10);
    initializer(w_xhg, in_dim*h_dim, 11);
    initializer(b_hf, h_dim, 12);
    initializer(b_hi, h_dim, 13);
    initializer(b_ho, h_dim, 14);
    initializer(b_hg, h_dim, 15);
    c_elapsed = rdtsc() - c_initial;
    s_elapsed = dsecnd() - s_initial;
    printf (" == Data initialization using Intel(R) MKL completed == \n"
            " == at %.5f milliseconds and %llu cycles== \n\n", (s_elapsed * 1000), c_elapsed);

    printf(" LSTM Computation\n\n");
    s_initial = dsecnd();
    c_initial = rdtsc();
    for(loop = 0; loop < LOOP; loop++){
        //ct (ft * ct-1)
        vsMul(h_dim, f, c, c);

        //ft 
        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    1, h_dim, in_dim, 1, x, in_dim, w_xhf, h_dim, 0, temp, h_dim);

        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    1, h_dim, h_dim, 1, h, h_dim, w_hhf, h_dim, 0, f, h_dim);

        vsAdd(h_dim, f, temp, f);
        vsAdd(h_dim, f, b_hf, f);

        vsExp(h_dim, f, f_exp);
        for(j = 0; j < h_dim; j++){
            f[j] = f_exp[j] + 1;
        }
        vsDiv(h_dim, f, f_exp, f);

        //it
        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    1, h_dim, in_dim, 1, x, in_dim, w_xhi, h_dim, 0, temp, h_dim);

        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    1, h_dim, h_dim, 1, h, h_dim, w_hhi, h_dim, 0, i, h_dim);

        vsAdd(h_dim, i, temp, i);
        vsAdd(h_dim, i, b_hi, i);

        vsExp(h_dim, i, i_exp);
        for(j = 0; j < h_dim; j++){
            i[j] = i_exp[j] + 1;
        }
        vsDiv(h_dim, i, i_exp, i);

        //ot
        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    1, h_dim, in_dim, 1, x, in_dim, w_xho, h_dim, 0, temp, h_dim);

        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    1, h_dim, h_dim, 1, h, h_dim, w_hho, h_dim, 0, o, h_dim);

        vsAdd(h_dim, o, temp, o);
        vsAdd(h_dim, o, b_ho, o);

        vsExp(h_dim, o, o_exp);
        for(j = 0; j < h_dim; j++){
            o[j] = o_exp[j] + 1;
        }
        vsDiv(h_dim, o, o_exp, o);
        
        //gt
        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    1, h_dim, in_dim, 1, x, in_dim, w_xhg, h_dim, 0, temp, h_dim);

        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    1, h_dim, h_dim, 1, h, h_dim, w_hhg, h_dim, 0, g, h_dim);

        vsAdd(h_dim, g, temp, g);
        vsAdd(h_dim, g, b_hg, g);

        vsTanh(h_dim, g, g);

        //ct
        vsMul(h_dim, i, g, temp);
        
        vsAdd(h_dim, c, temp, c);

        //ht
        vsTanh(h_dim, c, temp);

        vsMul(h_dim, temp, o, h); 
                
    }
    c_elapsed = (rdtsc() - c_initial) / LOOP;
    s_elapsed = (dsecnd() - s_initial) / LOOP;

    printf (" == MLP computation using Intel(R) MKL completed == \n"
            " == at %.5f milliseconds and %llu cycles == \n\n", (s_elapsed * 1000), c_elapsed);
    
    printf (" Deallocating memory \n\n");
    mkl_free(x);
    mkl_free(h);
    mkl_free(f);
    mkl_free(i);
    mkl_free(o);
    mkl_free(g);
    mkl_free(c);

    mkl_free(w_xhf);
    mkl_free(w_hhf);
    mkl_free(w_xhi);
    mkl_free(w_hhi);
    mkl_free(w_xho);
    mkl_free(w_hho);
    mkl_free(w_xhg);
    mkl_free(w_hhg);

    mkl_free(temp);

    mkl_free(b_hf);
    mkl_free(b_hi);
    mkl_free(b_ho);
    mkl_free(b_hg);

    c_t_elapsed = rdtsc() - c_t_initial;

    printf (" LSTM Benchmark completed in %llu cycles.\n\n", c_t_elapsed);
    return 0;


}