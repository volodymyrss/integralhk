import os,sys

if sys.version_info[0]!=2 or sys.version_info[1]<7:
    print("need python 2.7!")
    sys.exit(1)

environment_root=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

#################################################
# site configuration: to modify
#################################################

isdc_env=dict(
isdc_arc="/isdc/arc/rev_3",
isdc_nrt="/isdc/pvphase/nrt/ops",
#isdc_nrt="/isdc/arc/FTP/arc_distr/NRT/public/",
isdc_ref_cat="/dev/null",
isdc_env_root=os.environ['ISDC_ENV']#"/home/savchenk/local/osa/osa_sw-9.0"
)

daemon_spiacs=dict(
port=7431
)


smtp_info=dict(
host='localhost',
from_address='Volodymyr.Savchenko@unige.ch',
to_address='vladimir.savchenko@gmail.com'
)

################################################3
# package setup
#################################################

software_path=environment_root+"/software"

daemon_path=software_path+"/support/daemon"
server_path=software_path+"/spiacs/spiacs_server"
generators_path=software_path+"/spiacs/generators"

science_path=software_path+"/support/science"
other_path=software_path+"/support/other"

sys.path.append(daemon_path)
sys.path.append(server_path)
sys.path.append(generators_path)
sys.path.append(other_path)
sys.path.append(science_path)

dump_lc_path=software_path+"/spiacs/dump_lc"
dump_lc_binary=dump_lc_path+"/dump_lc"
sys.path.append(dump_lc_path)

################################################3

PYTHONPATH=":".join(sys.path)

if __name__=="__main__":
    if len(sys.argv)==2:
        print(eval(sys.argv[1]))

