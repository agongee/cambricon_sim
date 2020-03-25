CC = gcc
LDFLAGS = -Wl,--start-group ${MKLROOT}/lib/intel64/libmkl_intel_lp64.a ${MKLROOT}/lib/intel64/libmkl_sequential.a ${MKLROOT}/lib/intel64/libmkl_core.a -Wl,--end-group -lpthread -lm -ldl
TARGET = mlp_mkl cnn_mkl rnn_mkl lstm_mkl som_mkl autoencoder_mkl

all: $(TARGET)

mlp_mkl:
	$(CC) -o mlp_mkl mlp_mkl.c $(LDFLAGS)

cnn_mkl:
	$(CC) -o cnn_mkl cnn_mkl.c $(LDFLAGS)

rnn_mkl:
	$(CC) -o rnn_mkl rnn_mkl.c $(LDFLAGS)

lstm_mkl:
	$(CC) -o lstm_mkl lstm_mkl.c $(LDFLAGS)

som_mkl:
	$(CC) -o som_mkl som_mkl.c $(LDFLAGS)

autoencoder_mkl:
	$(CC) -o autoencoder_mkl autoencoder_mkl.c $(LDFLAGS)

clean:
	rm $(TARGET)