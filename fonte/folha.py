import sys,glob
from PIL import Image,ImageDraw
pasta,saida,ini,fim,W=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]) if len(sys.argv)>5 else 3
fs=sorted(glob.glob(pasta+'/*.jpg'))
fs=[f for f in fs if ini<=int(f.split('/')[-1][:2])<=fim]
th=(640,360);H=(len(fs)+W-1)//W
s=Image.new('RGB',(W*th[0],H*th[1]),'white')
for i,f in enumerate(fs):
    im=Image.open(f).resize(th);d=ImageDraw.Draw(im);d.text((6,6),f.split('/')[-1][:-4],fill='red');s.paste(im,((i%W)*th[0],(i//W)*th[1]))
s.save(saida,quality=80)
