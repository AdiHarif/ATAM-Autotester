AAT_print:
	pushq %rax
	pushq %rdx
	pushq %rsi
	pushq %rdi
	movq $1, %rax
	movq $1, %rdi
	pushq $AAT_out
	movq %rsp, %rsi
	movq $8, %rdx 
	syscall
	popq %rax
	movq $1, %rax
	movq $1, %rdi
	movq $AAT_out, %rsi
	movq $AAT_io_end-AAT_out, %rdx 
	syscall
	popq %rdi
	popq %rsi
	popq %rdx
	popq %rax

