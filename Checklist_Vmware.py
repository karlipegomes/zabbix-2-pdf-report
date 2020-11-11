from pyVim.connect import SmartConnectNoSSL, Disconnect
from datetime import datetime

c = SmartConnectNoSSL(host='<hostname_VMware>',user='VmApi@vsphere.local',pwd='<password>')

datacenter = c.content.rootFolder.childEntity[0]
alarms = datacenter.triggeredAlarmState


for i in alarms:
    print ('Definition: '+ i.entity.name)
    print(i.alarm.info.name)
    print(i.time)
    dt = datetime.fromisoformat(str(i.time))
    h = int(dt.strftime('%H'))
    h -= 3
    dt = dt.replace(hour=h)
    print(dt.ctime())
    
Disconnect(c)
