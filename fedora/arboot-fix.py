#!/usr/bin/python3
#from __future__ import print_function
import subprocess
import os
import sys
import time
import gettext
import random
import threading
import gi
gi.require_version("Gtk","3.0")
from gi.repository import Gtk,GdkPixbuf

project_location=os.path.dirname(os.path.split(os.path.abspath(__file__))[0])
icon=project_location+"/arboot-fix.png"
locale=project_location+"/locale"
print(locale)
gettext.install('arboot-fix',locale)

dirname = os.path.abspath(os.path.dirname(__file__))
subprocess.call("umount -f -R /mnt 2>/dev/null",shell=True)

os.makedirs("/mnt/arfedora_fix_boot",exist_ok=True)
#if not os.path.isdir("/mnt/arfedora_fix_boot"):
 #   os.mkdir("/mnt/arfedora_fix_boot")

subprocess.call("umount -f -R /mnt/arfedora_fix_boot 2>/dev/null",shell=True)

grub_install="grub2-install"            #for other distro chage this ex :grub-install
grub_mkconfig="grub2-mkconfig"          #for other distro chage this ex :grub-mkconfig
legacy = "/boot/grub2/grub.cfg"         #for other distro chage this ex :/boot/grub/grub.cfg
uefi = "/boot/efi/EFI/fedora/grub.cfg"  #for other distro chage this ex :/boot/grub/grub.cfg


use_internet=True #set False to remove Internet radio button
befor_chroot_efi_custom_command_if_use_internet_false=[]
in_chroot_efi_custom_command_if_use_internet_false=[]

#legacy_command=["dnf install  os-prober  grub2 kernel kernel-core kernel-modules kernel-modules-extra  --best -y --setopt=strict=0",
                #"dnf reinstall   os-prober  grub2 kernel kernel-core kernel-modules kernel-modules-extra --best -y --setopt=strict=0"]

#efi_command=["dnf install  shim os-prober efibootmgr grub2 grub2-efi* kernel kernel-core kernel-modules kernel-modules-extra --best -y --setopt=strict=0", \
             #"dnf reinstall shim os-prober efibootmgr grub2 grub2-efi* kernel kernel-core kernel-modules kernel-modules-extra --best -y --setopt=strict=0"]



legacy_command=["dnf install     os-prober  grub2  --best -y --setopt=strict=0",
                "dnf reinstall   os-prober  grub2  --best -y --setopt=strict=0"]

efi_command=["dnf install   shim os-prober efibootmgr grub2 grub2-efi*  --best -y --setopt=strict=0", \
             "dnf reinstall shim os-prober efibootmgr grub2 grub2-efi*  --best -y --setopt=strict=0"]




class NInfo(Gtk.MessageDialog):
    def __init__(self,message,parent=None):
        Gtk.MessageDialog.__init__(self,parent,1,Gtk.MessageType.INFO,Gtk.ButtonsType.OK,message)
        self.parent=parent
        self.set_transient_for(self.parent)
        self.set_modal(True)
        self.parent.set_sensitive(False)
        self.run()
        self.parent.set_sensitive(True)
        self.destroy()

def quit(w1=None,w2=None):
    subprocess.call("umount -f -R /mnt/arfedora_fix_boot 2>/dev/null", shell=True)
    Gtk.main_quit()

class MW(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self,resizable=False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_title(_("Arboot Fix"))
        self.check="d"
        self.y_o_n = False
        self.pwd=os.getcwd()
        self.all_par=[]
        self.all_root_par={}
        self.all_boot_par=[]
        self.all_efi_par=[]
        self.__get_all()
        self.backup_all_boot_par = self.all_boot_par
        self.backup_all_efi_par = self.all_efi_par
        self.internet=False
        if len(self.all_root_par) == 0 :
            NInfo(_("Linux Not Found"),self)
            self.destroy()
            sys.exit()

        self.notebook=Gtk.Notebook()
        self.add(self.notebook)
        self.page1=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.page1.set_border_width(10)
        self.label1=Gtk.Label(_("Boot Fix"))
        self.notebook.append_page(self.page1,self.label1)
        self.vbox1=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=20)
        self.page1.pack_start(self.vbox1,True,True,0)

        self.hbox1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.hbox2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.hbox3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.hbox4 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.hbox5 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.hbox6 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.hbox7 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.hbox8 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.vbox1.pack_start(self.hbox1,True,True,0)
        self.vbox1.pack_start(self.hbox2,True,True,0)
        self.vbox1.pack_start(self.hbox3,True,True,0)
        self.vbox1.pack_start(self.hbox4,True,True,0)
        self.vbox1.pack_start(self.hbox5,True,True,0)

        self.vbox2=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=5)
        self.vbox1.pack_start(self.vbox2,True,True,0)
        self.vbox2.pack_start(self.hbox6,True,True,0)
        self.vbox2.pack_start(self.hbox7,True,True,0)
        self.vbox2.pack_start(self.hbox8,True,True,0)

        self.rootlabel = Gtk.Label(_('Root Target:'))
        self.hbox1.pack_start(self.rootlabel, True, True, 0)
        self.root_target = Gtk.ComboBoxText(tooltip_text =_("Select Parttion"))
        self.root_target.props.width_request = 510
        self.hbox1.pack_start(self.root_target,True,True,0)
        self.rootrefresh=Gtk.Button(stock=Gtk.STOCK_REFRESH,tooltip_text=_("Refresh Device"))
        self.rootrefresh.connect('clicked', self.__root_refresh_target)
        self.hbox1.pack_start(self.rootrefresh, True, True, 0)

        self.__root_refresh_target()


        self.bootlabel = Gtk.Label(_('Boot Target:'))
        self.hbox2.pack_start(self.bootlabel, True, True, 0)
        self.boot_target = Gtk.ComboBoxText(tooltip_text =_("Select Parttion"))
        self.boot_target.props.width_request = 510
        self.hbox2.pack_start(self.boot_target, True, True, 0)
        self.bootrefresh = Gtk.Button(stock=Gtk.STOCK_REFRESH, tooltip_text=_("Refresh Device"))
        self.bootrefresh.connect('clicked', self.__boot_refresh_target)
        self.hbox2.pack_start(self.bootrefresh, True, True, 0)
        self.boot_target.set_sensitive(False)
        self.bootrefresh.set_sensitive(False)
        if len(self.all_boot_par) != 0:
            self.boot_target.set_sensitive(True)
            self.bootrefresh.set_sensitive(True)
            self.__boot_refresh_target()


        self.efilabel = Gtk.Label(_('EFI  Target:'))
        self.hbox3.pack_start(self.efilabel, True, True, 0)
        self.efi_target = Gtk.ComboBoxText(tooltip_text =_("Select Parttion"))
        if use_internet:
            self.efi_target.connect("changed",self.__on_efi_target_changed)
        self.efi_target.props.width_request = 510
        self.hbox3.pack_start(self.efi_target, True, True, 0)
        self.efirefresh = Gtk.Button(stock=Gtk.STOCK_REFRESH, tooltip_text=_("Refresh Device"))
        self.efirefresh.connect('clicked', self.__efi_refresh_target)
        self.hbox3.pack_start(self.efirefresh, True, True, 0)
        self.efi_target.set_sensitive(False)
        self.efirefresh.set_sensitive(False)
        if len(self.all_efi_par) != 0:
            self.efi_target.set_sensitive(True)
            self.efirefresh.set_sensitive(True)
            self.__efi_refresh_target()

        if use_internet:
            self.radio1 = Gtk.RadioButton(label=_("Without Internet"))
            self.radio1.connect("toggled",self.__radio1_toggle)
            self.radio2 = Gtk.RadioButton.new_with_label_from_widget(self.radio1,_("With Internet"))
            self.radio2.connect("toggled", self.__radio2_toggle)
            self.radio2.set_active(False)
            self.hbox4.pack_start(self.radio1, True, True, 0)
            self.hbox4.pack_start(self.radio2, True, True, 0)
            if len(self.all_efi_par) != 0:
                if self.efi_target.get_active_text() != "None":
                    self.radio2.set_active(True)
                    self.radio1.set_sensitive(False)
                    self.radio2.set_sensitive(False)
                    self.internet=True

        self.radio3 = Gtk.RadioButton(label=_("Auto Scan Parttions"))
        self.radio3.connect("toggled",self.__radio3_toggle)
        self.radio4 = Gtk.RadioButton.new_with_label_from_widget(self.radio3,_("Set Manual Parttions"))
        self.radio4.set_active(False)
        self.radio4.connect("toggled", self.__radio4_toggle)
        self.hbox5.pack_start(self.radio3, True, True, 0)
        self.hbox5.pack_start(self.radio4, True, True, 0)

        self.fix_button=Gtk.Button(label=_("Fix Grub Boot Loader"))
        self.fix_button.connect("clicked", self.__fix)
        self.hbox6.pack_start(self.fix_button,True,True,0)

        self.about_button=Gtk.Button(label=_("About"))
        self.about_button.connect("clicked", self.__about)
        self.hbox7.pack_start(self.about_button,True,True,0)


        self.exit_button=Gtk.Button(label=_("Exit"))
        self.exit_button.connect("clicked",quit)
        self.hbox8.pack_start(self.exit_button,True,True,0)


    def __fix(self,button):
        self.check="d"
        self.y_o_n = False
        efi_legacy=0
        if len(self.all_efi_par) != 0:
            if self.efi_target.get_active_text()!="None":
                efi_legacy += 3

        if len(self.all_boot_par) != 0:
            if self.boot_target.get_active_text()!="None":
                efi_legacy += 2


        check = self.Yes_Or_No(_("Are you sure do you want continue?"))
        if not check:
            return

        self.set_sensitive(False)
        if efi_legacy==0:
            t1 = threading.Thread(target=self.legacy_root_fix)
            t1.start()
            t1.join()

        elif efi_legacy==2:
            if self.boot_target.get_active_text() == "None":
                t1 = threading.Thread(target=self.legacy_root_fix)
                t1.start()
                t1.join()
            else:
                t1 = threading.Thread(target=self.legacy_root_with_boot_fix)
                t1.start()
                t1.join()

        elif efi_legacy==3:
            if self.efi_target.get_active_text() == "None":
                t1 = threading.Thread(target=self.legacy_root_fix)
                t1.start()
                t1.join()
            else:
                t1 = threading.Thread(target=self.efi_root_fix)
                t1.start()
                t1.join()

        elif efi_legacy == 5:
            if self.boot_target.get_active_text() == "None" and  self.efi_target.get_active_text() == "None":
                t1 = threading.Thread(target=self.legacy_root_fix)
                t1.start()
                t1.join()

            elif self.boot_target.get_active_text() == "None":
                t1 = threading.Thread(target=self.efi_root_fix)
                t1.start()
                t1.join()

            elif self.efi_target.get_active_text() == "None":
                t1 = threading.Thread(target=self.legacy_root_with_boot_fix)
                t1.start()
                t1.join()
            else:
                t1 = threading.Thread(target=self.efi_root_with_boot_fix)
                t1.start()
                t1.join()



        if self.check == "d":
            NInfo(_("Done"),self)
        elif self.check == "i":
            NInfo(_("Error Check Your Connection"),self)
        elif self.check == "m":
            NInfo(_("Fail"),self)
        self.set_sensitive(True)



    def __root_refresh_target(self, *args):
        count=0
        self.root_target.get_model().clear()
        for k in  self.all_root_par.keys():
            self.root_target.append_text(k)
            count+=1
        self.root_target.set_active(random.choice(range(count)))

    def __boot_refresh_target(self, *args):
        count=0
        self.boot_target.get_model().clear()
        if "None" not in self.boot_target.get_model() and len(self.all_boot_par) != 0:
            self.boot_target.append_text("None")
            count+=1
        for f in  self.all_boot_par:
            self.boot_target.append_text(f)
            count += 1

        while True:
            r = random.choice(range(count))
            self.boot_target.set_active(r)
            if self.boot_target.get_active_text() != "None":
                break

    def __efi_refresh_target(self, *args):
            count=0
            self.efi_target.get_model().clear()
            if "None" not in self.efi_target.get_model() and len(self.all_efi_par) != 0:
                self.efi_target.append_text("None")
                count+=1
            for f in  self.all_efi_par:
                self.efi_target.append_text(f)
                count+=1
            while True:
                r = random.choice(range(count))
                self.efi_target.set_active(r)
                if self.efi_target.get_active_text() != "None":
                    break




    def legacy_root_fix(self):
        print("\nFix ROOT\n")
        root=self.all_root_par[self.root_target.get_active_text()]
        check = subprocess.call("mount  %s /mnt/arfedora_fix_boot 2>/dev/null" % root, shell=True)
        if check!=0:
            self.check = "m"
            return False
        time.sleep(0.2)
        for i in ["/dev", "/proc", "/sys", "/run", "/dev/pts"]:
            time.sleep(0.2)
            check = subprocess.call("mount  -B %s /mnt/arfedora_fix_boot%s" % (i, i), shell=True)
            if check != 0:
                self.check = "m"
                return False

        real_root = os.open("/", os.O_RDONLY)
        os.chroot("/mnt/arfedora_fix_boot")
        os.chdir("/boot")
        if self.internet:
            check = subprocess.call(legacy_command[0],shell=True)
            if check != 0:
                self.check = "i"
                return False
            check = subprocess.call(legacy_command[1],shell=True)
            if check != 0:
                self.check = "i"
                return False

        check = subprocess.call("%s --force /dev/sda"%grub_install, shell=True)
        if check!=0:
            self.check = "m"
            return  False
        check = subprocess.call("%s -o  %s"%(grub_mkconfig,legacy), shell=True)
        if check!=0:
            self.check = "m"
            return  False
        os.fchdir(real_root)
        os.chroot(".")
        os.close(real_root)
        subprocess.call("umount -f -R /mnt/arfedora_fix_boot 2>/dev/null", shell=True)
        return True

    def legacy_root_with_boot_fix(self):
        print("\nFix ROOT/BOOT\n")

        root=self.all_root_par[self.root_target.get_active_text()]
        boot=self.boot_target.get_active_text()
        check = subprocess.call("mount  %s /mnt/arfedora_fix_boot 2>/dev/null" % root, shell=True)
        if check!=0:
            self.check = "m"
            return False
        time.sleep(0.2)
        check = subprocess.call("mount  %s /mnt/arfedora_fix_boot/boot 2>/dev/null" % boot, shell=True)
        if check!=0:
            self.check = "m"
            return False
        time.sleep(0.2)
        for i in ["/dev", "/proc", "/sys", "/run", "/dev/pts"]:
            time.sleep(0.2)
            check = subprocess.call("mount  -B %s /mnt/arfedora_fix_boot%s" % (i, i), shell=True)
            if check != 0:
                self.check = "m"
                return False

        real_root = os.open("/", os.O_RDONLY)
        os.chroot("/mnt/arfedora_fix_boot")
        os.chdir("/boot")

        if self.internet:
            check = subprocess.call(legacy_command[0],shell=True)
            if check != 0:
                self.check = "i"
                return False
            check = subprocess.call(legacy_command[1],shell=True)
            if check != 0:
                self.check = "i"
                return False

        check = subprocess.call("%s --force /dev/sda"%grub_install, shell=True)
        if check!=0:
            self.check = "m"
            return False
        check = subprocess.call("%s -o  %s"%(grub_mkconfig,legacy), shell=True)
        if check!=0:
            self.check = "m"
            return False
        os.fchdir(real_root)
        os.chroot(".")
        os.close(real_root)
        subprocess.call("umount -f -R /mnt/arfedora_fix_boot 2>/dev/null", shell=True)
        return True

    def efi_root_fix(self):
        print("\nFix ROOT/EFI\n")
        root=self.all_root_par[self.root_target.get_active_text()]
        efi=self.efi_target.get_active_text()
        check = subprocess.call("mount  %s /mnt/arfedora_fix_boot 2>/dev/null" % root, shell=True)
        if check!=0:
            self.check = "m"
            return  False
        time.sleep(0.2)
        check = subprocess.call("mount  %s /mnt/arfedora_fix_boot/boot/efi 2>/dev/null" % efi, shell=True)
        if check!=0:
            self.check = "m"
            return  False
        time.sleep(0.2)
        for i in ["/dev", "/proc", "/sys", "/run", "/dev/pts"]:
            time.sleep(0.2)
            check = subprocess.call("mount  -B %s /mnt/arfedora_fix_boot%s" % (i, i), shell=True)
            if check != 0:
                self.check = "m"
                return False

        if not use_internet:
            if len(in_chroot_efi_custom_command_if_use_internet_false) != 0:
                for c in in_chroot_efi_custom_command_if_use_internet_false:
                    time.sleep(0.5)
                    check = subprocess.call("%s" % i, shell=True)
                    if check != 0:
                        self.check = "m"
                        return False


        real_root = os.open("/", os.O_RDONLY)
        os.chroot("/mnt/arfedora_fix_boot")
        os.chdir("/boot")
        if self.internet:
            check = subprocess.call(efi_command[0],shell=True)
            if check != 0:
                self.check = "i"
                return False
            check= subprocess.call(efi_command[1],shell=True)
            if check != 0:
                self.check = "i"
                return False
        else:
            if len(befor_chroot_efi_custom_command_if_use_internet_false) != 0:
                for c in befor_chroot_efi_custom_command_if_use_internet_false:
                    time.sleep(0.5)
                    check = subprocess.call("%s"%i, shell=True)
                    if check != 0:
                        self.check = "m"
                        return False

        check = subprocess.call("%s  -o %s"%(grub_mkconfig,uefi), shell=True)
        if check!=0:
            self.check = "m"
            return  False
        os.fchdir(real_root)
        os.chroot(".")
        os.close(real_root)
        subprocess.call("umount -f -R /mnt/arfedora_fix_boot 2>/dev/null", shell=True)
        return True


    def efi_root_with_boot_fix(self):
        print("\nFix ROOT/BOOT/EFI\n")
        root=self.all_root_par[self.root_target.get_active_text()]
        efi=self.efi_target.get_active_text()
        boot=self.boot_target.get_active_text()
        check = subprocess.call("mount  %s /mnt/arfedora_fix_boot 2>/dev/null" % root, shell=True)
        if check!=0:
            self.check = "m"
            return  False
        time.sleep(0.2)
        check = subprocess.call("mount  %s /mnt/arfedora_fix_boot/boot 2>/dev/null" % boot, shell=True)
        if check!=0:
            self.check = "m"
            return  False
        time.sleep(0.2)
        check = subprocess.call("mount  %s /mnt/arfedora_fix_boot/boot/efi 2>/dev/null" % efi, shell=True)
        if check!=0:
            self.check = "m"
            return  False
        time.sleep(0.2)
        for i in ["/dev", "/proc", "/sys", "/run", "/dev/pts"]:
            time.sleep(0.2)
            check = subprocess.call("mount  -B %s /mnt/arfedora_fix_boot%s" % (i, i), shell=True)
            if check != 0:
                self.check = "m"
                return False

        if not use_internet:
            if len(in_chroot_efi_custom_command_if_use_internet_false) != 0:
                for c in in_chroot_efi_custom_command_if_use_internet_false:
                    time.sleep(0.5)
                    check = subprocess.call("%s" % i, shell=True)
                    if check != 0:
                        self.check = "m"
                        return False

        real_root = os.open("/", os.O_RDONLY)
        os.chroot("/mnt/arfedora_fix_boot")
        os.chdir("/boot")
        if self.internet:
            check = subprocess.call(efi_command[0],shell=True)
            if check != 0:
                self.check = "i"
                return False
            check = subprocess.call(efi_command[1],shell=True)
            if check != 0:
                self.check = "i"
                return False
        else:
            if len(befor_chroot_efi_custom_command_if_use_internet_false) != 0:
                for c in befor_chroot_efi_custom_command_if_use_internet_false:
                    time.sleep(0.5)
                    check = subprocess.call("%s" % i, shell=True)
                    if check != 0:
                        self.check = "m"
                        return False

        check = subprocess.call("%s  -o %s"%(grub_mkconfig,uefi), shell=True)
        if check!=0:
            self.check = "m"
            return  False
        os.fchdir(real_root)
        os.chroot(".")
        os.close(real_root)
        subprocess.call("umount -f -R /mnt/arfedora_fix_boot 2>/dev/null", shell=True)
        return True

    def __on_efi_target_changed(self,c):
        if self.efi_target.get_active_text() != "None":
            self.radio2.set_active(True)
            self.radio1.set_sensitive(False)
            self.radio2.set_sensitive(False)
            self.internet = True
        else:
            self.radio1.set_sensitive(True)
            self.radio2.set_sensitive(True)


    def get_distro_name(self,f):
        with open(f) as myfile:
            for line in myfile.readlines():
                if line.startswith("ID"):
                    return line.split("=")[1].strip()

    def get_all_parrtions(self):
        all_parttions = subprocess.check_output("lsblk -l -n -p -o  \"NAME\"", shell=True).decode('utf-8').split("\n")
        result = []
        for i in all_parttions:
            if len(i) == 0:
                continue
            if i.startswith("/dev/") and len(i) > 8 and not i.startswith("/dev/sr") and not i.startswith("/dev/mapper/live") and not i.startswith("/dev/loop"):
                try:
                    time.sleep(0.3)
                    subprocess.call("mount  %s /mnt/arfedora_fix_boot 2>/dev/null" % i, shell=True)
                    print(i)
                    result.append(i)
                except:
                    continue
                finally:
                    time.sleep(0.3)
                    subprocess.call("umount -f -R /mnt/arfedora_fix_boot 2>/dev/null", shell=True)
        self.all_par=result

    def get_linux_root_parrtions(self):
        result = {}
        count = 0
        for i in self.all_par:
            time.sleep(0.3)
            subprocess.call("mount  %s /mnt/arfedora_fix_boot 2>/dev/null" % i, shell=True)
            if os.path.isfile("/mnt/arfedora_fix_boot/etc/os-release"):
                print (i)
                result.setdefault("%s ==> %s" % (i, self.get_distro_name("/mnt/arfedora_fix_boot/etc/os-release")), i)
            time.sleep(0.3)
            subprocess.call("umount -f -R /mnt/arfedora_fix_boot 2>/dev/null", shell=True)
        self.all_root_par=result

    def get_linux_boot_parrtions(self):
        result = []
        for i in self.all_par:
            time.sleep(0.3)
            subprocess.call("mount  %s /mnt/arfedora_fix_boot 2>/dev/null" % i, shell=True)
            if os.path.isdir("/mnt/arfedora_fix_boot/grub2"):
                print(i)
                result.append(i)
            time.sleep(0.3)
            subprocess.call("umount -f -R /mnt/arfedora_fix_boot 2>/dev/null", shell=True)
        self.all_boot_par=result

    def get_linux_efi_parrtions(self):
        result = []
        for i in self.all_par:
            time.sleep(0.3)
            subprocess.call("mount  %s /mnt/arfedora_fix_boot 2>/dev/null" % i, shell=True)
            if os.path.isdir("/mnt/arfedora_fix_boot/EFI"):
                print(i)
                result.append(i)
            time.sleep(0.3)
            subprocess.call("umount -f -R /mnt/arfedora_fix_boot 2>/dev/null", shell=True)
        self.all_efi_par=result

    def __get_all(self):
        print ("\nGet ALl Parrtions :")
        self.get_all_parrtions()
        print("\nGet ALl Root Parrtions :")
        self.get_linux_root_parrtions()
        print("\nGet ALl Boot Parrtions :")
        self.get_linux_boot_parrtions()
        print("\nGet ALl EFI Parrtions :")
        self.get_linux_efi_parrtions()

    def __radio1_toggle(self,b=None):
        self.internet=False
        print ("Internet is : ")
        print (self.internet)

    def __radio2_toggle(self,b=None):
        self.internet=True
        print ("Internet is : ")
        print (self.internet)

    def __radio3_toggle(self,b=None):
        self.all_boot_par=self.backup_all_boot_par
        self.all_efi_par=self.backup_all_efi_par
        if len(self.all_boot_par) != 0:
            self.__boot_refresh_target()
        else:
            self.boot_target.get_model().clear()
            self.boot_target.set_sensitive(False)
            self.bootrefresh.set_sensitive(False)

        if len(self.all_efi_par) != 0:
            self.__efi_refresh_target()
        else:
            self.efi_target.get_model().clear()
            self.efi_target.set_sensitive(False)
            self.efirefresh.set_sensitive(False)

        if use_internet:
            self.radio1.set_sensitive(True)
            self.radio2.set_sensitive(True)

    def __radio4_toggle(self,b=None):
        self.all_boot_par=self.all_par
        self.all_efi_par=self.all_par
        self.boot_target.set_sensitive(True)
        self.bootrefresh.set_sensitive(True)
        self.efi_target.set_sensitive(True)
        self.efirefresh.set_sensitive(True)
        self.__boot_refresh_target()
        self.__efi_refresh_target()

    def __about(self,b):
        authors = ["Youssef Sourani <youssef.m.sourani@gmail.com>"]
        about = Gtk.AboutDialog()
        about.set_transient_for(self)
        about.set_program_name("Arboot fix")
        about.set_version("0.1beta")
        about.set_copyright("Copyright © 2017 Youssef Sourani")
        about.set_comments(_("Arboot is a simple tool for fix grub bootloader"))
        about.set_website("http://www.arfedora.blogspot.com")
        about.set_website_label(_('My Website'))
        about.set_logo(GdkPixbuf.Pixbuf.new_from_file(icon))
        about.set_authors(authors)
        about.set_license_type(Gtk.License.GPL_3_0)
        translators = _("translator-credit")
        if translators != "translator-credits":
            about.set_translator_credits(translators)
        about.run()
        about.destroy()

    def Yes_Or_No(self,message):

        d = Gtk.MessageDialog(parent=self,
                              flags=Gtk.DialogFlags.MODAL,
                              type=Gtk.MessageType.QUESTION,
                              buttons=Gtk.ButtonsType.OK_CANCEL,
                             message_format=message)
        rrun = d.run()
        if rrun == Gtk.ResponseType.OK:
            self.y_o_n = True
            d.destroy()
            return True
        else:
            d.destroy()
            return False



def main():
    mw=MW()
    mw.connect("delete-event", quit)
    mw.show_all()
    Gtk.main()

if __name__ == "__main__" :
    main()

