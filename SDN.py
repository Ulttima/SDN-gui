from Tkinter import *
import Image
import ImageTk
import requests
import time

controller_ipaddr = '10.241.142.99'
polling_interval = 15


class Switch:
    
    def __init__(self, switch_DPID, switch_Port_Count):
        self.switch_DPID = switch_DPID
        self.switch_Port_Count = switch_Port_Count
        
        if self.switch_Port_Count == 48:
            self.switch_Image = ImageTk.PhotoImage(Image.open("Switches/Images/switch48.JPG"))
        elif self.switch_Port_Count == 4:
            self.switch_Image = ImageTk.PhotoImage(Image.open("Switches/Images/switch4.JPG"))
        else:
            self.switch_Image = ImageTk.PhotoImage(Image.open("Switches/Images/panda.JPG"))

        
switch_url = 'http://%s:8080/wm/core/controller/switches/json' % (controller_ipaddr)
print 'URL:', switch_url

#switch_list_current_dpid = []
#switch_list_update_dpid = []
device_dict = {}

#GUI bits
root = Tk()
canvas = Canvas(root, width = 640, height = 640, relief = SUNKEN, background = '#fff')
canvas.pack(fill = BOTH, expand = 1)

#initial startup poll and switch object creation
switch_json = requests.get(switch_url)
switch_list = switch_json.json()

number_of_switches = len(switch_list)

while number_of_switches > 0:
    switch = switch_list[(number_of_switches-1)]
    switch_dpid = switch['dpid']
    number_of_ports = switch['ports']
    number_of_ports = len(number_of_ports)
    device_dict[switch_dpid] = Switch(switch_dpid, number_of_ports)
    number_of_switches = number_of_switches - 1

print 'Switches connected at startup:', device_dict

print 'device_dict keys:', device_dict.keys()

for key in device_dict.keys():
    print device_dict[key].switch_DPID
    print device_dict[key].switch_Port_Count

x = 10
y = 10
for key in device_dict:
    canvas.create_image(x, y, anchor = NW, image = device_dict[key].switch_Image, tags = key)
    y += 110

print '--------------------------------------------------------'

#Event Binds
wgrabbed = False
wtag = ""
wxyoffset = (0, 0)

def lclick(event):
    if canvas.find_withtag(CURRENT):
        global wgrabbed, wtag, wxyoffset
        wgrabbed = True
        wtag = canvas.gettags(CURRENT)[0]
        cornerxy = canvas.coords(wtag)     #Location of image NW corner
        wxyoffset = (event.x - cornerxy[0], event.y - cornerxy[1])     #Offset of click event location and image NW corner
        #print wxyoffset
        #print "click", wtag

def lmotion(event):
    if wgrabbed:
        newxy = (event.x - wxyoffset[0], event.y - wxyoffset[1])     #Image placement with offset
        canvas.coords(wtag, newxy)
    #print "motion", wtag

def lrelease(event):
    global wgrabbed
    
    if wgrabbed:
        #newxy = (event.x, event.y)     #Image placement with no offset
        newxy = (event.x - wxyoffset[0], event.y - wxyoffset[1])     #Image placement with offset
        canvas.coords(wtag, newxy)
        wgrabbed = False
        #print "release", wtag, " postion:", (event.x, event.y)

#polling mainloop start
def switch_poll():
    #current switches

    switch_list_current_dpid = []
    switch_list_update_dpid = []
        
    switch_json = requests.get(switch_url)
    switch_list_current = switch_json.json()
    
    number_of_switches_current = len(switch_list_current)
       
    while number_of_switches_current > 0:
        switch = switch_list_current[(number_of_switches_current) - 1]
        switch_dpid = switch['dpid']
        switch_list_current_dpid.append(switch_dpid)
        number_of_switches_current = number_of_switches_current - 1

    print "Current switches from JSON:",switch_list_current_dpid, time.ctime()

    #updated switches
    switch_json = requests.get(switch_url)
    switch_list_update = switch_json.json()
    
    number_of_switches_update = len(switch_list_update)
    
    while number_of_switches_update > 0:
        switch = switch_list_update[(number_of_switches_update) - 1]
        switch_dpid = switch['dpid']
        switch_list_update_dpid.append(switch_dpid)
        number_of_switches_update = number_of_switches_update - 1

    print "Updated switches from JSON:", switch_list_update_dpid, time.ctime()
    
    def listdiff(list1, list2):
        common = set(list1).union(set(list2))
        difference = set(list1).intersection(set(list2))
        return list(common - difference)

    switch_change = listdiff(switch_list_current_dpid, switch_list_update_dpid)

    print "Difference in switches", switch_change

    switch_change_value = set(switch_list_current_dpid).issubset(set(switch_list_update_dpid))
    print "Subset:", switch_change_value
    print "Length:", len(switch_change)

    if switch_change_value and len(switch_change)!= 0:
        for item in switch_change:
            for item in switch_list_update:
                switch_dpid = item['dpid']
                number_of_ports = item['ports']
                number_of_ports = len(number_of_ports)
                device_dict[switch_dpid] = Switch(switch_dpid, number_of_ports)
        print 'switch is new'
        print 'device_dict:'
        for key in device_dict.keys():
            print device_dict[key].switch_DPID
            print device_dict[key].switch_Port_Count
        print '--------------------------------------------------------'        
    elif len(switch_change) == 0:
        print 'no switch change'
        print 'device_dict:'
        for key in device_dict.keys():
            print device_dict[key].switch_DPID
            print device_dict[key].switch_Port_Count
        print '--------------------------------------------------------'
    else:
        for item in switch_change:
            del device_dict[item]            
        print 'switch was removed'
        print 'device_dict:'
        for key in device_dict.keys():
            print device_dict[key].switch_DPID
            print device_dict[key].switch_Port_Count
        print '--------------------------------------------------------'       

    #switch_list_current_dpid = []
    #switch_list_update_dpid = []

    root.after(polling_interval * 1000, switch_poll) 

#Event bind bits
canvas.bind("<Button-1>", lclick)
canvas.bind("<B1-Motion>", lmotion)
canvas.bind("<ButtonRelease-1>", lrelease)

switch_poll()
root.mainloop()
