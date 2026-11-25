const frame=document.getElementById('generator'),status=document.getElementById('status'),unavailable=document.getElementById('unavailable');
const timeout=setTimeout(()=>{status.hidden=true;unavailable.hidden=false;},15000);
frame.addEventListener('load',()=>{clearTimeout(timeout);status.hidden=true;unavailable.hidden=true;});
frame.addEventListener('error',()=>{clearTimeout(timeout);status.hidden=true;unavailable.hidden=false;});
