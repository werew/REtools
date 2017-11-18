"""
This convenience gdb script was borrowed 
from one of gynvael's stream:
    https://www.youtube.com/watch?v=Jk5Yad598vs
    https://drive.google.com/drive/u/0/folders/0B5y5AGVPzpIOd2s3aUJRc2VJX0E

I just modified some minor parts.
So, thanks gynvael :)

Also, don't forget to check out his blog:
http://gynvael.coldwind.pl/
"""
import gdb
import sys
import struct
import re

PC = "$eip"
MY_BP_HANDLERS = {}

def ExprAsInt(expr):
  return int(str(gdb.parse_and_eval("(void*)(%s)" % expr )).split(" ")[0], 16)

def BreakHandler(ev):
  global MY_BP_HANDLERS

  eip = ExprAsInt(PC)
  print("~"*70, hex(eip))
  
  if ev.__class__ != gdb.BreakpointEvent:

    print("Not a breakpoint; not handled")
    print(gdb.execute("info reg", False, True))

    eip = ExprAsInt(PC)
    print(gdb.execute("where 10", False, True))
    sys.exit(0)

  for bp in ev.breakpoints:
    if eip in MY_BP_HANDLERS:
      MY_BP_HANDLERS[eip](ev.breakpoints, eip)
    else:
      print("----> Unknown BP!")
      print(gdb.execute("x/1i %s" % PC, False, True))

def SetBP(addr, handler):
  gdb.execute("break *0x%x" % addr, False)
  MY_BP_HANDLERS[addr] = handler

# Set some stuff.
gdb.execute("set python print-stack full", False, True)    
gdb.execute("set disassembly-flavor intel", False)
gdb.execute("set height 0", False)
gdb.events.stop.connect(BreakHandler)

# Initialize PC
file_type = re.findall(r".*file type (\S+).", 
              gdb.execute("info target", False, True))[0]
if file_type == "elf64-x86-64":
  PC = "$rip"
elif file_type == "elf32-i386":
  PC = "$eip"
else:
  print(":( Unkown file_type: %s" % file_type)


# Main debug loop
def main():
  THE_END = False
  while not THE_END:
    try:
      gdb.execute("c")
    except gdb.error as detail:
      if str(detail) == "The program is not being run.":
        THE_END = True
      else:
        raise

############ Add your handlers below #############

# Example: 
#
# fff = open("in.eips", "w")
# def log(ev, eip):
#  global fff
#  fff.write("%.8x\n" % eip)
#
# SetBP(0x401000, log)
# SetBP(0x401C9C, log)
# SetBP(0x401DE4, log)
# ...

gdb.execute("r arg1 arg2 ...", False)
main()

