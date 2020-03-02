#include <linux/module.h>
#include <linux/kernel.h>

void enable_ccr (void *info)
{
	//set the user enable register bit to 0
	asm volatile ("mcr p15, 0, %0, c9, c14, 0" :: "r" (1));
	//Enable all counters in the PNMC control-register
	asm volatile ("mcr p15, 0, %0, c9, c12, 0\t\n" ::"r"(1));
	//Enable cycle count specifically
	//bit 31:enable cycle count
	//bits 0-3: enable performance counters 0 -3
	asm volatile ("mcr p15, 0, %0, c9, c12, 1\t\n" :: "r"(0x80000000));
}

int init_module(void) 
{
	on_each_cpu (enable_ccr, NULL, 0);
	printk (KERN_INFO "Userspace access to CCR enabled");
	return 0;
}

void cleanup_module(void) {
}

