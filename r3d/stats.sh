cd /opt/r3d/out; for f in ${@:-test_ev*.png}; do ffmpeg -v error -y -i $f -vf scale=48:64,format=rgb24 -f rawvideo t.raw; python3 -c "
import sys;d=open('t.raw','rb').read(); W,H=48,64; ch=' .:-=+*#%@'
print('==', sys.argv[1])
for t in range(3):
  seg=d[t*W*H//3*3:(t+1)*W*H//3*3]; print('third',t,[sum(seg[i::3])//(len(seg)//3) for i in range(3)])
if len(sys.argv)>2:
  for y in range(0,H,2): print(''.join(ch[min(9,sum(d[(y*W+x)*3:(y*W+x)*3+3])//77)] for x in range(W)))
" $f $ASCII; done
