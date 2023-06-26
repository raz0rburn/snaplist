#uses https://github.com/vmware/pyvmomi

#this script checks vcenter for virtual machine snapshots and send list of snapshots to telegram
#require these components: 
apt install python3-pip
#telegram lib for python
pip3 install pyTelegramBotAPI
#Vmware lib for python
pip3 install pyVmomi
