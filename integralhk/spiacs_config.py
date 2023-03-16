import os
import sys
import shutil

if sys.version_info[0]!=3 or sys.version_info[1]<5:
    print("need python 3!")
    sys.exit(1)

environment_root=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

#################################################
# site configuration: to modify
#################################################


isdc_env=dict(
isdc_arc=os.environ.get("REP_BASE_PROD_ARC", "/isdc/arc/rev_3"),
isdc_nrt=os.environ.get("REP_BASE_PROD_NRT","/isdc/pvphase/nrt/ops"),
isdc_rt=os.environ.get("REP_RT","/data/realtime"),
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

dump_lc_path = os.getenv('DUMP_LC_PATH', software_path+"/spiacs/dump_lc")
dump_lc_binary = os.getenv('DUMP_LC_BINARY', shutil.which("dump_lc"))
sys.path.append(dump_lc_path)

################################################3

PYTHONPATH=":".join(sys.path)

if __name__=="__main__":
    if len(sys.argv)==2:
        print((eval(sys.argv[1])))

