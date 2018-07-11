# -*- coding: utf-8 -*-


import sys,os
#currUser =  pwd.getpwuid(os.getuid())[0]
#if currUser == 'behinger':
#    PROJECT_ROOT = '/net/store/nbp/users/behinger/projects'
#elif currUser == 'agert':
#    PROJECT_ROOT = '/net/store/nbp/users/agert/nbp_pupiltools'
#else:
#    os.path.join(os.path.realpath(os.path.dirname(__file__)), os.pardir,os.pardir)
    
#sys.path.append(PROJECT_ROOT)
#sys.path.append(,"./lib/opencv2/"))
#sys.path.append("../lib/ceres/lib"))
#sys.path.append(os.path.join(PROJECT_ROOT,"/net/store/nbp/users/behinger/tmp/ceres-solver/build2/include/"))
#sys.path.append(os.path.join(PROJECT_ROOT,"/net/store/nbp/users/behinger/tmp/ceres-solver/build2/lib/"))
#sys.path.append(os.path.join(PROJECT_ROOT,"./code/recalibration/"))
#sys.path.append(os.path.join(PROJECT_ROOT,"./code/"))#

sys.path.append(os.path.abspath("../lib/pupil/pupil_src/shared_modules/calibration_routines"))
sys.path.append(os.path.abspath("../lib/pupil/pupil_src/shared_modules/"))
sys.path.append(os.path.abspath("../lib/pupil/pupil_src/player/"))
sys.path.append(os.path.abspath("../lib/opencv2"))
sys.path.append(os.path.abspath("../lib/glfw3"))
sys.path.append(os.path.abspath("../"))
sys.path.append(os.path.abspath("../code"))
sys.path.append(os.path.abspath("../lib/nslr-hmm"))
sys.path.append(os.path.abspath("../lib/pyedfread/lib"))
sys.path.append(os.path.abspath("../code/functions/fake_pl_loading"))

import pandas as pd
pd.options.display.max_columns = 30