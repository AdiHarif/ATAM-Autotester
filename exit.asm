AAT_exit:
    mov $60, %rax
    mov $0, %rdi
    syscall
AAT_fin:
    nop