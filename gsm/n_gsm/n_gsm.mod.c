#include <linux/module.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

MODULE_INFO(vermagic, VERMAGIC_STRING);
MODULE_INFO(name, KBUILD_MODNAME);

__visible struct module __this_module
__attribute__((section(".gnu.linkonce.this_module"))) = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

#ifdef RETPOLINE
MODULE_INFO(retpoline, "Y");
#endif

static const struct modversion_info ____versions[]
__used
__attribute__((section("__versions"))) = {
	{ 0x6681337c, __VMLINUX_SYMBOL_STR(module_layout) },
	{ 0x8653a238, __VMLINUX_SYMBOL_STR(param_ops_int) },
	{ 0x2c0090f5, __VMLINUX_SYMBOL_STR(tty_unregister_driver) },
	{ 0x67b27ec1, __VMLINUX_SYMBOL_STR(tty_std_termios) },
	{ 0x4b40b3e1, __VMLINUX_SYMBOL_STR(put_tty_driver) },
	{ 0xe29e1294, __VMLINUX_SYMBOL_STR(tty_register_driver) },
	{ 0xffd80df3, __VMLINUX_SYMBOL_STR(tty_set_operations) },
	{ 0xa120d33c, __VMLINUX_SYMBOL_STR(tty_unregister_ldisc) },
	{ 0xe9a97149, __VMLINUX_SYMBOL_STR(__tty_alloc_driver) },
	{ 0x27628ec0, __VMLINUX_SYMBOL_STR(tty_register_ldisc) },
	{ 0x558f4e5e, __VMLINUX_SYMBOL_STR(register_netdev) },
	{ 0x328a05f1, __VMLINUX_SYMBOL_STR(strncpy) },
	{ 0x4f67f2b3, __VMLINUX_SYMBOL_STR(alloc_netdev_mqs) },
	{ 0xc6cbbc89, __VMLINUX_SYMBOL_STR(capable) },
	{ 0x54fd31e0, __VMLINUX_SYMBOL_STR(skb_queue_head) },
	{ 0xec3c5240, __VMLINUX_SYMBOL_STR(netif_rx) },
	{ 0x10ebb306, __VMLINUX_SYMBOL_STR(skb_put) },
	{ 0x3dd5d31, __VMLINUX_SYMBOL_STR(__netdev_alloc_skb) },
	{ 0xf4fa543b, __VMLINUX_SYMBOL_STR(arm_copy_to_user) },
	{ 0x28cc25db, __VMLINUX_SYMBOL_STR(arm_copy_from_user) },
	{ 0xf4553c9, __VMLINUX_SYMBOL_STR(n_tty_ioctl_helper) },
	{ 0xfa2a45e, __VMLINUX_SYMBOL_STR(__memzero) },
	{ 0x5400dd6a, __VMLINUX_SYMBOL_STR(tty_register_device) },
	{ 0xd4805d7b, __VMLINUX_SYMBOL_STR(tty_unregister_device) },
	{ 0xf68f9be9, __VMLINUX_SYMBOL_STR(tty_vhangup) },
	{ 0x12a68f38, __VMLINUX_SYMBOL_STR(tty_port_lower_dtr_rts) },
	{ 0xf4502961, __VMLINUX_SYMBOL_STR(tty_port_close_end) },
	{ 0x783cd624, __VMLINUX_SYMBOL_STR(tty_port_close_start) },
	{ 0xde102425, __VMLINUX_SYMBOL_STR(free_netdev) },
	{ 0xd4bc2d3c, __VMLINUX_SYMBOL_STR(unregister_netdev) },
	{ 0xb05fb62d, __VMLINUX_SYMBOL_STR(tty_wakeup) },
	{ 0xb210c120, __VMLINUX_SYMBOL_STR(tty_flip_buffer_push) },
	{ 0x1cfce253, __VMLINUX_SYMBOL_STR(tty_insert_flip_string_fixed_flag) },
	{ 0x575675fe, __VMLINUX_SYMBOL_STR(tty_kref_put) },
	{ 0x361c7457, __VMLINUX_SYMBOL_STR(tty_port_tty_get) },
	{ 0x1786750a, __VMLINUX_SYMBOL_STR(tty_hangup) },
	{ 0xfe9ca102, __VMLINUX_SYMBOL_STR(__tty_insert_flip_char) },
	{ 0xf23fcb99, __VMLINUX_SYMBOL_STR(__kfifo_in) },
	{ 0xf1504265, __VMLINUX_SYMBOL_STR(skb_queue_tail) },
	{ 0x59d0a29d, __VMLINUX_SYMBOL_STR(skb_dequeue_tail) },
	{ 0xb81edb68, __VMLINUX_SYMBOL_STR(__dev_kfree_skb_any) },
	{ 0xafbc4b89, __VMLINUX_SYMBOL_STR(skb_pull) },
	{ 0x13d0adf7, __VMLINUX_SYMBOL_STR(__kfifo_out) },
	{ 0x12da5bb2, __VMLINUX_SYMBOL_STR(__kmalloc) },
	{ 0xa24b783a, __VMLINUX_SYMBOL_STR(tty_port_block_til_ready) },
	{ 0x883cbb4d, __VMLINUX_SYMBOL_STR(tty_port_tty_set) },
	{ 0xc374d5b3, __VMLINUX_SYMBOL_STR(tty_port_hangup) },
	{ 0xda02d67, __VMLINUX_SYMBOL_STR(jiffies) },
	{ 0xa38caae0, __VMLINUX_SYMBOL_STR(mod_timer) },
	{ 0x16305289, __VMLINUX_SYMBOL_STR(warn_slowpath_null) },
	{ 0xd697e69a, __VMLINUX_SYMBOL_STR(trace_hardirqs_on) },
	{ 0xec3d2e1b, __VMLINUX_SYMBOL_STR(trace_hardirqs_off) },
	{ 0x27e1a049, __VMLINUX_SYMBOL_STR(printk) },
	{ 0xddece99e, __VMLINUX_SYMBOL_STR(__init_waitqueue_head) },
	{ 0x8cc776c4, __VMLINUX_SYMBOL_STR(tty_write_room) },
	{ 0x76046a0f, __VMLINUX_SYMBOL_STR(tty_hung_up_p) },
	{ 0x1e047854, __VMLINUX_SYMBOL_STR(warn_slowpath_fmt) },
	{ 0x869e9831, __VMLINUX_SYMBOL_STR(tty_name) },
	{ 0xd7d22e9f, __VMLINUX_SYMBOL_STR(tty_port_tty_hangup) },
	{ 0x413c0466, __VMLINUX_SYMBOL_STR(__wake_up) },
	{ 0x78ca661a, __VMLINUX_SYMBOL_STR(skb_dequeue) },
	{ 0xc9356e41, __VMLINUX_SYMBOL_STR(consume_skb) },
	{ 0xdb760f52, __VMLINUX_SYMBOL_STR(__kfifo_free) },
	{ 0x5c2e3421, __VMLINUX_SYMBOL_STR(del_timer) },
	{ 0x5fc262cb, __VMLINUX_SYMBOL_STR(mutex_unlock) },
	{ 0x6a0a5e65, __VMLINUX_SYMBOL_STR(tty_port_install) },
	{ 0x195a71c2, __VMLINUX_SYMBOL_STR(mutex_lock) },
	{ 0xc38c1cd, __VMLINUX_SYMBOL_STR(kmalloc_caches) },
	{ 0xde6c254e, __VMLINUX_SYMBOL_STR(tty_port_init) },
	{ 0x5ee52022, __VMLINUX_SYMBOL_STR(init_timer_key) },
	{ 0xc068440e, __VMLINUX_SYMBOL_STR(__kfifo_alloc) },
	{ 0x201a4b32, __VMLINUX_SYMBOL_STR(__mutex_init) },
	{ 0x6ac38045, __VMLINUX_SYMBOL_STR(kmem_cache_alloc_trace) },
	{ 0xc269a62f, __VMLINUX_SYMBOL_STR(tty_port_put) },
	{ 0x30e74134, __VMLINUX_SYMBOL_STR(tty_termios_copy_hw) },
	{ 0x963e0acd, __VMLINUX_SYMBOL_STR(finish_wait) },
	{ 0x93f6bff1, __VMLINUX_SYMBOL_STR(prepare_to_wait_event) },
	{ 0x1000e51, __VMLINUX_SYMBOL_STR(schedule) },
	{ 0xfe487975, __VMLINUX_SYMBOL_STR(init_wait_entry) },
	{ 0xa1c76e0a, __VMLINUX_SYMBOL_STR(_cond_resched) },
	{ 0x34908c14, __VMLINUX_SYMBOL_STR(print_hex_dump_bytes) },
	{ 0x9d669763, __VMLINUX_SYMBOL_STR(memcpy) },
	{ 0x37a0cba, __VMLINUX_SYMBOL_STR(kfree) },
	{ 0x2e5810c6, __VMLINUX_SYMBOL_STR(__aeabi_unwind_cpp_pr1) },
	{ 0xb1ad28e0, __VMLINUX_SYMBOL_STR(__gnu_mcount_nc) },
};

static const char __module_depends[]
__used
__attribute__((section(".modinfo"))) =
"depends=";


MODULE_INFO(srcversion, "033810CB1068F5156BB12B4");
