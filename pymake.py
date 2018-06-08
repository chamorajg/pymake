import json
from pprint import pprint

name=''
cflags=''
common_CFLAGS=''
cpu_includes=''
cppflags=''
cpu_sources=''
final_sources=''
ldflags=''
json_data = dict()
data = dict()
fileContents = ''
make_include = ''

def output():
    print("Makefile Generated Successfully")


def read():
    global data, fileContents, json_data
    with open('Libcutils-Android.json') as json_file:
        json_data = json.load(json_file)


def write(fileContents):
    global data, json_data
    filename = input("Enter the name of the makefile")
    makefile = open(filename+'.mk','w')
    makefile.write(fileContents)
    makefile.close


def sources():
    global data,fileContents,json_data,name,source,final_sources,cpu_sources,make_include
    for data in json_data:
        if 'cc_library' in data.keys():
            name = 'NAME = '+data['cc_library']['name']
            source = 'SOURCES = '

            if 'srcs' in data['cc_library']:
                data['cc_library']['srcs'].sort()
                for j in data['cc_library']['srcs']:
                    source+= '\t\t\t'+j+'\\'+'\n'

            if 'arch' in data['cc_library'].keys():
                for j in data['cc_library']['arch'].keys():
                    cpu_sources+= j+'_SOURCES = '
                    for k in data['cc_library']['arch'][j]['srcs']:
                        cpu_sources+= '\t\t\t'+k+' '+'\\'+'\n'
                final_sources = 'SOURCES+= $($($(DEB_HOST_ARCH)_SOURCES))'

            if 'target' in data['cc_library'].keys():
                if 'android' in data['cc_library']['target'].keys():
                    if 'srcs' in data['cc_library']['target']['android'].keys():
                        data['cc_library']['target']['android']['srcs'].sort()
                        for i in (data['cc_library']['target']['android']['srcs']):
                            source+= '\t\t\t'+i+'\\'+'\n'
    print(name)
    print(source)
    #Can be added if wanted
    #make_include = input('Enter name of the other makefiles to be includec')
    fileContents+= name+'\n'+source+'\n'+cpu_sources+'\n'+final_sources

def ldFlags():
    global data, fileContents, json_data,ldflags
    ldflags+= 'LDFLAGS += -shared -Wl,-soname,'
    #These LDFLAGS are found in almost all makefiles so I have written it by default
    for data in json_data:
        if 'cc_library' in data.keys():
            if 'target' in data['cc_library'].keys():
                if 'linux' in data['cc_library']['target'].keys():
                    ldflags = 'LDFLAGS+= '

                    if 'ldflags' in data['cc_library']['target']['linux'].keys():
                        for i in data['cc_library']['target']['linux']['ldflags']:
                            ldflags+= i + ' '

                    if 'host_ldlibs' in data['cc_library']['target']['linux'].keys():
                         for i in data['cc_library']['target']['linux']['host_ldlibs']:
                             ldflags+= i + ' '
    print(ldflags)
    fileContents+= '\n'+ldflags

def  cFlags():
    #Cflags - any changes write it here in comments
    global data, fileContents, json_data,cflags,common_CFLAGS
    for data in json_data:
        if 'common_CFLAGS' in data.keys():
            for i in data['common_CFLAGS']:
                common_CFLAGS += ' ' + i

        if 'cc_defaults' in data.keys():
            if data['cc_defaults']['cflags'] == 'common_CFLAGS':
                cflags += 'CFLAGS +=' + common_CFLAGS
            else:
                cflags = 'CFLAGS+= '
                for j in data['cc_defaults']['cflags']:
                    cflags+= j + ' '
    print(cflags)
    fileContents+= '\n'+cflags

def cppFlags():
    #Cppflags - there are certain cppflags in almost all makefiles so I have written it here. Changes in comments
    global data, fileContents, json_data,cppflags,cpu_includes
    cppflags+='CPPFLAGS +='
    cppflags+= '-Iinclude -Idebian/include'
    for data in json_data:
        if 'cc_defaults' in data.keys():
            if 'arch' in data['cc_defaults'].keys():
                cpu_includes = ''
                for j in data['cc_defaults']['arch'].keys():
                    cpu_includes+= j+'_SOURCES = '
                    for k in data['cc_defaults']['arch'][j]['local_include_dirs']:
                        cpu_includes+='\t\t\t'+k+' '+'\\'+'\n'
                cppflags = 'CPPFLAGS+= $($(CPU)_INCLUDES)) '

            if 'local_include_dirs' in data['cc_defaults'].keys():
                for j in data['cc_defaults']['local_include_dirs']:
                    cppflags+= '-I'+j+' '
    print(cppflags)
    fileContents+= '\n'+cpu_includes+'\n'+cppflags


def Build():
    #build-build file requires the directory where the target is to be created. So target directory is taken as input and build function is written
    global data, fileContents, json_data,command
    print('CSOURCES := $(foreach source,$(filter %.c,$(SOURCES), libcutils/$(source)) ')
    print('CPPSOURCES := $(foreach source,$(filter %.cpp,$(SOURCES), libcutils/$(source)) ')
    command = input("Enter the directory you want to build\n")
    if command == '':
        command = command
    else :
        command = command+'/'
    print('build: ' + '$(SOURCES)' + '\n\t\t' + '$(CC) $^ -o ' + command + '$(NAME) $(CFLAGS) $(CPPFLAGS) $(LDFLAGS)')
    fileContents+= '\n'+'CSOURCES := $(foreach source,$(filter %.c,$(SOURCES),'+command+'$(source)) '+'\n'+'CPPSOURCES := $(foreach source,$(filter %.cpp,$(SOURCES), '+command+'$(source)) '+'\n'+'build: ' + '$(SOURCES)' + '\n\t\t' + '$(CC) $^ -o ' + command + '$(NAME) $(CFLAGS) $(CPPFLAGS) $(LDFLAGS)'

    #print('CPU_SOURCES',cpu_sources)
    #print('FINAL_SOURCES',final_sources)
    #print('CPU_INCLUDES',cpu_includes)



def Clean():
    #clean- Changes required can be commented
    global data, fileContents, json_data
    print('\n'+'clean: $(RM) '+command+'$(NAME)')
    fileContents+= '\n'+'clean: $(RM) '+command+'$(NAME)'

def start():
    global data, fileContents, json_data
    read()
    sources()
    cFlags()
    cppFlags()
    ldFlags()
    Build()
    Clean()
    write(fileContents)
    output()
    exit(0)

start()
