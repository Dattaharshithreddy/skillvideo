B=/opt/r3d/blender/blender
$B -b --command extension install-file -r user_default -e /opt/r3d/assets/mpfb.zip 2>&1 | tail -2
$B -b --factory-startup -P /opt/r3d/sv/r3d/probe_mpfb.py 2>&1 | grep -E 'OPS|USERDATA|SYSDATA|Error|error' | head
