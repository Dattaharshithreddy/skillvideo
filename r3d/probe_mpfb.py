import bpy, addon_utils, sys
bpy.ops.preferences.addon_enable(module='bl_ext.user_default.mpfb')
ops = [o for o in dir(bpy.ops.mpfb)]
print('OPS', [o for o in ops if any(k in o for k in ('pack','load','human','cloth','skin','hair','pose','rig','eye'))])
from bl_ext.user_default.mpfb.services.locationservice import LocationService
print('USERDATA', LocationService.get_user_data())
print('SYSDATA', LocationService.get_mpfb_data())
