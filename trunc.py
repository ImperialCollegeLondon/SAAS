"""
A function to truncate a number according to its uncertainty and return a tuple of
of a 14-character string containing the number and a 10-character string containing
its uncertainty. For use in a program made to format a table, it may be
desireable to strip off some of the blank spaces as follows:

(BF,BFunc) = trunc(BF,BFunc)
print(BF[4:-2],BFunc[2:-3])

This was not included in the function to maintain flexibilty for use with wavelengths,
wavenumbers, energy levels, branching fractions, and transition probabilities.

LICENSE:

NIST-developed software is provided by NIST as a public service. You may use, copy, and 
distribute copies of the software in any medium, provided that you keep intact this entire 
notice. You may improve, modify, and create derivative works of the software or any portion 
of the software, and you may copy and distribute such modifications or works. Modified works 
should carry a notice stating that you changed the software and should note the date and 
nature of any such change. Please explicitly acknowledge the National Institute of Standards 
and Technology as the source of the software. 

NIST-developed software is expressly provided "AS IS." NIST MAKES NO WARRANTY OF ANY KIND, 
EXPRESS, IMPLIED, IN FACT, OR ARISING BY OPERATION OF LAW, INCLUDING, WITHOUT LIMITATION, THE 
IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT, AND 
DATA ACCURACY. NIST NEITHER REPRESENTS NOR WARRANTS THAT THE OPERATION OF THE SOFTWARE WILL BE 
UNINTERRUPTED OR ERROR-FREE, OR THAT ANY DEFECTS WILL BE CORRECTED. NIST DOES NOT WARRANT OR 
MAKE ANY REPRESENTATIONS REGARDING THE USE OF THE SOFTWARE OR THE RESULTS THEREOF, INCLUDING 
BUT NOT LIMITED TO THE CORRECTNESS, ACCURACY, RELIABILITY, OR USEFULNESS OF THE SOFTWARE.

You are solely responsible for determining the appropriateness of using and distributing the 
software and you assume all risks associated with its use, including but not limited to the 
risks and costs of program errors, compliance with applicable laws, damage to or loss of data, 
programs or equipment, and the unavailability or interruption of operation. This software is 
not intended to be used in any situation where a failure could cause risk of injury or damage 
to property. The software developed by NIST employees is not subject to copyright protection 
within the United States.

"""

def trunc(val,unc):
    if unc>2.5 :
        newunc= "%3.0f       " % float(unc)
        newval= "%7.0f       " % float(val)       
    elif unc>0.25 :
        newunc= "%5.1f     " % float(unc)
        newval= "%9.1f     " % float(val)       
    elif unc>0.025 :
        newunc= "%6.2f    " % float(unc)
        newval= "%10.2f    " % float(val)      
    elif unc>0.0025:
        newunc= "%7.3f   " % float(unc)
        newval= "%11.3f   " % float(val)      
    elif unc>0.00025:
        newunc= "%8.4f  " % float(unc)
        newval= "%12.4f  " % float(val)      
    elif unc>0.000025:
        newunc= "%9.5f " % float(unc)
        newval= "%13.5f " % float(val)      
    else :
        newunc= "%10.6f" % float(unc)
        newval= "%14.6f" % float(val)     
    return(newval,newunc)
