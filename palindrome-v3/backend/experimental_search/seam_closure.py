"""Exact gap invariant. This validates letters, not English grammar."""
from .bilateral_seams import debt
from .validator import normalize

def gap_state(left,right):
 d=debt(left,right)
 if not d['compatible']:return {'admitted':False,'debt':d}
 residual_left=d['letters']if d['side']=='left'else''
 residual_right=d['letters'][::-1]if d['side']=='right'else''
 return {'admitted':True,'debt':d,'residual_left':residual_left,'residual_right':residual_right,'matched_outer_letters':d['matched']}

def close_gap(left,insertion,right):
 s=gap_state(left,right)
 if not s['admitted']:return {**s,'exact':False}
 residual=s['residual_left']+normalize(insertion)+s['residual_right']
 exact=residual==residual[::-1]
 tape=normalize(left+insertion+right)
 assert exact==(tape==tape[::-1])
 return {**s,'exact':exact,'residual':residual,'text':left+insertion+right,'letters':len(tape),'center_index':len(tape)//2,'odd':bool(len(tape)%2)}
