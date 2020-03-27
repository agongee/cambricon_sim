#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#include <mkl.h>

#define LOOP 20

uint64_t rdtsc(){
    uint64_t lo,hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((uint64_t)hi << 32) | lo;
}

int main(){
    float *in, *c1, *s1, *s1_re, *c2, *s2, *f1, *f2, *out; // activations
    float *in_c1, *s1_c2, *s2_f1, *f1_f2, *f2_out; // wegihts
    float *in_col, *s1_col, *s2_col;
    float *c1_exp, *c2_exp, *f1_exp, *f2_exp, *out_exp; // exponential, sigmoid
    float *f1_b, *f2_b, *out_b; // bias
    float *one;
    int in_dim, c1_dim, s1_dim, s1_re_dim, c2_dim, s2_dim, f1_dim, f2_dim, out_dim; 
    int in_c1_dim, s1_c2_dim, s2_f1_dim, f1_f2_dim, f2_out_dim;
    int loop, i, j;
    double s_initial, s_elapsed;
    uint64_t c_initial, c_elapsed, c_t_initial, c_t_elapsed;

    c_t_initial = rdtsc();

    in_dim = 28*28*5*5;
    c1_dim = 28*28*6;
    s1_dim = 14*14*6;
    s1_re_dim = 10*10*6*5*5;
    c2_dim = 16*10*10;
    s2_dim = 16*5*5;
    f1_dim = 120;
    f2_dim = 84;
    out_dim = 10;

    in_c1_dim = 6*1*5*5;
    s1_c2_dim = 16*6*5*5;
    s2_f1_dim = 400*120;
    f1_f2_dim = 120*84;
    f2_out_dim = 84*10;

    one = (float *)mkl_malloc(c1_dim*sizeof(float), 32);
    for(i = 0; i < c1_dim; i++){
        one[i] = 1;
    }
    
    in = (float *)mkl_malloc(in_dim*sizeof(float), 32);
    c1 = (float *)mkl_malloc(c1_dim*sizeof(float), 32);
    s1 = (float *)mkl_malloc(s1_dim*sizeof(float), 32);
    s1_re = (float *)mkl_malloc(s1_re_dim*sizeof(float), 32);
    c2 = (float *)mkl_malloc(c2_dim*sizeof(float), 32);
    s2 = (float *)mkl_malloc(s2_dim*sizeof(float), 32);
    f1 = (float *)mkl_malloc(f1_dim*sizeof(float), 32);
    f2 = (float *)mkl_malloc(f2_dim*sizeof(float), 32);
    out = (float *)mkl_malloc(out_dim*sizeof(float), 32);

    c1_exp = (float *)mkl_malloc(c1_dim*sizeof(float), 32);
    c2_exp = (float *)mkl_malloc(c2_dim*sizeof(float), 32);
    f1_exp = (float *)mkl_malloc(f1_dim*sizeof(float), 32);
    f2_exp = (float *)mkl_malloc(f2_dim*sizeof(float), 32);
    out_exp = (float *)mkl_malloc(out_dim*sizeof(float), 32);

    in_c1 = (float *)mkl_malloc(in_c1_dim*sizeof(float), 32);
    s1_c2 = (float *)mkl_malloc(s1_c2_dim*sizeof(float), 32);
    s2_f1 = (float *)mkl_malloc(s2_f1_dim*sizeof(float), 32);
    f1_f2 = (float *)mkl_malloc(f1_f2_dim*sizeof(float), 32);
    f2_out = (float *)mkl_malloc(f2_out_dim*sizeof(float), 32);

    printf(" Initializing Input and Weight Data\n\n");
    s_initial = dsecnd();
    c_initial = rdtsc();
    for(i = 0; i < in_dim; i++){
        in[i] = (float)(i+1);
    }

    for(i = 0; i < in_c1_dim; i++){
        in_c1[i] = (float)(i+2);
    }

    for(i = 0; i < s1_c2_dim; i++){
        s1_c2[i] = (float)(i+3);
    }

    for(i = 0; i < s2_f1_dim; i++){
        s2_f1[i] = (float)(i+4);
    }

    for(i = 0; i < f1_f2_dim; i++){
        f1_f2[i] = (float)(i+5);
    }

    for(i = 0; i < f2_out_dim; i++){
        f2_out[i] = (float)(i+6);
    }

    for(i = 0; i < s1_re_dim; i++){
        s1_re[i] = (float)(i+7);
    }
    c_elapsed = rdtsc() - c_initial;
    s_elapsed = dsecnd() - s_initial;
    printf (" == Data initialization using Intel(R) MKL completed == \n"
            " == at %.5f milliseconds and %llu cycles== \n\n", (s_elapsed * 1000), c_elapsed);

    printf(" CNN Computation\n\n");
    s_initial = dsecnd();
    c_initial = rdtsc();
    for(loop = 0; loop < LOOP; loop++){
        // in -> c1
        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    6, 28*28, 5*5, 1, in_c1, 5*5, in, 28*28, 0, c1, 28*28);
        vsExp(c1_dim, c1, c1_exp);
        vsAdd(c1_dim, c1_exp, one, c1);
        vsDiv(c1_dim, c1, c1_exp, c1);

        // c1 -> s1
        for(i = 0; i < 14; i++){
            for(j = 0; j < 14; j++){
                int index, c1_index;
                int a;

                index = (i*14 + j)*6;
                c1_index = (i*56 + j*2) * 6;
                
                for(a = 0; a < 6; a++){
                    s1[index+a] = c1[c1_index+a];
                }

                c1_index = c1_index + 6;

                for(a = 0; a < 6; a++){
                    s1[index+a] = c1[c1_index+a] > s1[index+a] ? c1[c1_index+a] : s1[index+a];
                }

                c1_index = c1_index - 6 + 28 * 14;

                for(a = 0; a < 6; a++){
                    s1[index+a] = c1[c1_index+a] > s1[index+a] ? c1[c1_index+a] : s1[index+a];
                }

                c1_index = c1_index + 6;

                for(a = 0; a < 6; a++){
                    s1[index+a] = c1[c1_index+a] > s1[index+a] ? c1[c1_index+a] : s1[index+a];
                }               
                
            }
        }

        // s1 -> c2
        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    16, 10*10, 5*5*6, 1, s1_c2, 5*5*6, s1_re, 10*10, 0, c2, 10*10);
        vsExp(c2_dim, c2, c2_exp);
        vsAdd(c2_dim, c2_exp, one, c2);
        vsDiv(c2_dim, c2, c2_exp, c2);

        // c2 -> s2
        for(i = 0; i < 5; i++){
            for(j = 0; j < 5; j++){
                int index, c2_index;
                int a;

                index = (i*5 + j)*16;
                c2_index = (i*20 + j*2) * 16;
                
                for(a = 0; a < 16; a++){
                    s2[index+a] = c2[c2_index+a];
                }

                c2_index = c2_index + 16;

                for(a = 0; a < 16; a++){
                    s2[index+a] = c2[c2_index+a] > s2[index+a] ? c2[c2_index+a] : c2[index+a];
                }

                c2_index = c2_index - 16 + 10 * 5;

                for(a = 0; a < 16; a++){
                    s2[index+a] = c2[c2_index+a] > s2[index+a] ? c2[c2_index+a] : c2[index+a];
                }

                c2_index = c2_index + 16;

                for(a = 0; a < 16; a++){
                    s2[index+a] = c2[c2_index+a] > s2[index+a] ? c2[c2_index+a] : c2[index+a];
                }               
                
            }
        }

        // c2 -> f1(120)
        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    1, f1_dim, s2_dim, 1, s2, s2_dim, s2_f1, f1_dim, 1, f1, f1_dim);
        vsExp(f1_dim, f1, f1_exp);
        vsAdd(f1_dim, f1_exp, one, f1);
        vsDiv(f1_dim, f1, f1_exp, f1);


        // f1(120) -> f2(84)
        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    1, f2_dim, f1_dim, 1, f1, f1_dim, f1_f2, f2_dim, 1, f2, f2_dim);
        vsExp(f2_dim, f2, f2_exp);
        vsAdd(f2_dim, f2_exp, one, f2);
        vsDiv(f2_dim, f2, f2_exp, f2);


        // f2(84) -> out(10)
        cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                    1, out_dim, f2_dim, 1, f2, f2_dim, f2_out, out_dim, 1, out, out_dim);
        vsExp(out_dim, out, out_exp);
        vsAdd(out_dim, out_exp, one, out);
        vsDiv(out_dim, out, out_exp, out);


    }
    c_elapsed = (rdtsc() - c_initial) / LOOP;
    s_elapsed = (dsecnd() - s_initial) / LOOP;
    printf (" == CNN computation using Intel(R) MKL completed == \n"
            " == at %.5f milliseconds and %llu cycles == \n\n", (s_elapsed * 1000), c_elapsed);

    mkl_free(in);
    mkl_free(c1);
    mkl_free(s1);
    mkl_free(s1_re);
    mkl_free(c2);
    mkl_free(s2);
    mkl_free(f1);
    mkl_free(f2);
    mkl_free(out);

    mkl_free(c1_exp);
    mkl_free(c2_exp);
    mkl_free(f1_exp);
    mkl_free(f2_exp);
    mkl_free(out_exp);

    mkl_free(in_c1);
    mkl_free(s1_c2);
    mkl_free(s2_f1);
    mkl_free(f1_f2);
    mkl_free(f2_out);

    c_t_elapsed = rdtsc() - c_t_initial;

    printf (" CNN Benchmark completed in %llu cycles.\n\n", c_t_elapsed);
    return 0;

}