const API=import.meta.env.VITE_API_URL||"http://127.0.0.1:8000";
export async function api(path,options={}){
 const controller=new AbortController(); const timeout=setTimeout(()=>controller.abort(),12000);
 try{
  const headers={"Content-Type":"application/json",...(options.headers||{})};
  const t=localStorage.getItem("orbyta_token"); if(t) headers["X-User-Token"]=t;
  const res=await fetch(`${API}${path}`,{method:options.method||"GET",headers,body:options.body,signal:controller.signal});
  const text=await res.text(); let data={}; try{data=text?JSON.parse(text):{}}catch{data={detail:text}};
  if(!res.ok)throw new Error(data.detail||`Request failed (${res.status})`);
  return data;
 }catch(err){if(err.name==="AbortError")throw new Error("Server took too long to respond. Make sure the Orbyta backend is running.");if(err instanceof TypeError)throw new Error("Cannot connect to Orbyta backend. Start FastAPI on port 8000.");throw err}
 finally{clearTimeout(timeout)}
}
