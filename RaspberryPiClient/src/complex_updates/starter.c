#include <getopt.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#define _GNU_SOURCE
#include <sched.h>

/*
 * constant variables required for acceptig inline arguments
 */
static const char* short_options = "hn:f:s:i";
static struct option long_options[] = {
	{"help", no_argument, 0, 'h'},
	{"nthreads",required_argument, 0, 'n'},
	{"saveresults", required_argument, 0, 's'},
	{"instcyclecount", no_argument, 0, 'i'},
	{0,0,0,0}
};
static const char *usagec[] = {
"Options:",
"	-h/--help			This message",
"	-n/--nthreads		Number of threads executing this program.",
"	-s/--saveresults	Save results in the specified filename",
"	-i/--instcyclecount	Count the number of instruction cycles",
};

/*
 * Forward declare function
 */
int psuedomain ();
void usage();

/*
 * Help function to describe the usage of the inline arguments
 */
void usage () {
	int i;
	for (i = 0; i < sizeof(usagec) / sizeof(usagec[0]); i++) {
		printf("%s\n",usagec[i]);
	}
}

/*
 * Read the current value of the CPU cycle count register
 */
static inline unsigned cctn_read(void) {
	unsigned cc;
	asm volatile ("mrc p15, 0, %0, c9, c13, 0" : "=r" (cc));
	return cc;
}



int main(int argc, char** argv )
{	
	int c_id = 0;
	char *c_str = "1", *freq_b = "1000Mhz", freq_command[60] = "", freq_reset[60] = "", *filenameptr = "./results/complex_updates.csv";
	unsigned int iter = 5;
	int nthreads = 1, j;
	unsigned long startTime = 0, endTime = 0, execTime = 0;
	FILE *ptr;
	int cyclecount = 0;
	unsigned long int dataloop_cv = 0;
	int *dataCachePointer = NULL;
	int dataCacheValue = 0;
	
	while (1) {
		int opt_idx = 0;
		int c = getopt_long(argc, argv, short_options, long_options, &opt_idx);
		if (c == -1) {
			break;			
		}

		switch (c) {
			case 0:
					break;
			case 'h': usage();
					goto bail;
			case 'n' : nthreads = atoi(optarg);
					break;
			case 's' : filenameptr = optarg;
					break;
			case 'i' : cyclecount = 1;
					break;
			default : usage();
					goto bail;
		}	
	}
	
	dataCachePointer = calloc(262144, sizeof(int));
	for(dataloop_cv = 0; dataloop_cv < 262144; dataloop_cv++) {
		dataCachePointer[dataloop_cv] = dataloop_cv;
	}
	
	ptr = fopen(filenameptr,"a");
	
	for (j = 0; j < nthreads; j++) {
		//execute an object
		if(cyclecount == 1) {
			startTime = cctn_read();
			psuedomain();
			endTime = cctn_read();
			execTime = execTime + endTime - startTime;
		}
		else {
			psuedomain();
		}
		
		//clear data caches
		for(dataloop_cv = 0; dataloop_cv < 262144; dataloop_cv++) {
			dataCacheValue = dataCachePointer[dataloop_cv];
		}
	}
	fprintf(ptr,"%lu ,",execTime);
	fprintf(ptr,"\n");
	free(dataCachePointer);
	
	bail:
	fclose(ptr);
	return 0;
}
