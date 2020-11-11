import pprint
from pyzabbix import ZabbixAPI
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Spacer
from reportlab.platypus import Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


ZABBIX_SERVER = 'http://<hostname>/'
USER = '<username>'
PASSWD = '<password>'
zapi = ZabbixAPI(ZABBIX_SERVER)
zapi.login(USER,PASSWD)
severity=['Not Classified','Information','Warning','Average','High','Disaster']


### Funcao para coletar problemas de um grupo de hosts do Zabbix ###
def getProblems(group_host):
    try:
        triggers = zapi.trigger.get(active=1,skipDependent=1,monitored=1,only_true=1,
                                    withLastEventUnacknowledged=1,selectHosts=['host'],
                                    expandDescription=1,group=group_host,sortfield=['priority'],
                                    sortorder=['DESC'],output=['description','priority'])
    except:
        print("Erro ao obter alertas do grupo " + group_host)
        return None

    alertList = []
    for i in triggers:
        problems = {}
        problems['Host'] = i['hosts'][0]['host']
        problems['Problem'] = i['description']
        problems['Severity'] = severity[int(i['priority'])]
        alertList.append(problems)
        #print(i['hosts'][0]['host'] + ': ' + i['description'] + ' ' + 'Severity: ' + severity[int(i['priority'])] + '\n')

    return alertList


### Create pdf table ###
def CreateTable(triggers):
    header = ['Host','Problem','Severity']
    data=[]
    data.append(header)
    for i in triggers:
        rowTable = []
        rowTable.append(i['Host'])
        rowTable.append(i['Problem'])
        rowTable.append(i['Severity'])
        data.append(rowTable)
        
    
    table = Table(data,colWidths=[200,300,'*'])
    style = TableStyle([
        ('BACKGROUND', (0,0), (3,0), colors.gray),
        ('TEXTCOLOR', (0,0),(-1,0),colors.whitesmoke),
        ('ALIGN', (0,0), (-1,0),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Courier-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ])

    coord = 0
    for j in data:
        if j[2] == 'Severity':
            coord += 1
            continue
        elif j[2] == 'Disaster':
            style.add('BACKGROUND', (-1,coord),(-1,coord), colors.red)
            coord += 1
        elif j[2] == 'High':
            style.add('BACKGROUND', (-1,coord),(-1,coord), colors.red)
            coord += 1
        elif j[2] == 'Average':
            style.add('BACKGROUND', (-1,coord),(-1,coord), colors.orange)
            coord += 1
        elif j[2] == 'Warning':
            style.add('BACKGROUND', (-1,coord),(-1,coord), colors.yellow)
            coord += 1
        else:
            style.add('BACKGROUND', (-1,coord),(-1,coord), colors.blue)
            coord += 1

    # Add borders
    style.add('GRID', (0,0), (-1,-1), 0.25, colors.black)

    table.setStyle(style)

    return table




########## Main Code ##########
GroupAlerts = ['Windows servers', 'Linux servers', 'Zabbix servers','Equipamentos de Rede', 'Firewall', 'EquipamentosWifi', 'Telefonia']

styles = getSampleStyleSheet()
styleN = styles['Heading2']
elems = []
for k in GroupAlerts:
    Alertas = getProblems(k)
    pprint.pprint(Alertas)
    table = CreateTable(Alertas)
    elems.append(Paragraph(k,styleN))
    elems.append(table)
    elems.append(Spacer(0,10))

zapi.user.logout()
fileName = 'pdfTable.pdf'
pdf = SimpleDocTemplate(fileName,pagesize=letter)
pdf.build(elems)
