import re
from .validator import normalize
def shape(text):
 """Same v3 wire shape, with punctuation-aware letter offsets."""
 words=re.findall(r"[A-Za-z]+",text);word_count=len(text.split());total=len(normalize(text));half=total//2;start=0
 for i,word in enumerate(words):
  n=len(normalize(word));end=start+n
  if total%2==0 and end==half:
   return dict(left=words[:i+1],center='',right=words[i+1:],centerDisplay='',pivot=0,pivotOdd=False,promptCenter=False,letters=total,words=word_count)
  if start<=half<end:
   wanted=half-start;offset=0;seen=0
   for offset,char in enumerate(word):
    if char.isascii() and char.isalpha():
     if seen==wanted:break
     seen+=1
   return dict(left=words[:i],center=word,right=words[i+1:],centerDisplay=word,pivot=offset,pivotOdd=bool(total%2),promptCenter=False,letters=total,words=word_count)
  start=end
 raise ValueError('Empty or invalid shape')
