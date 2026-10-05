const msg = (text) =>
    document.getElementById('msg').textContent=text||'';

async function api(path,opts){
    try{
        const res=await fetch(path,opts);
        const data=await res.json();

        if(!res.ok){
            msg(data.error);
            return null
        }
        msg();
        return data        
    }catch(err){
        msg("Could not access the server...!!")
        return null
    }

    }

const json = (method,body) => (
    {
        method:method,
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify(body)
    });

const load = async() =>{
    const items=await api('/inventory');
    if(!items){
        return
    };
    document.getElementById('rows').innerHTML=items.map(i=>`
        <tr>
            <td>${i.id}</td>
            <td>${i.product.product_name}<br><small>${i.product.brands||''}</small></td>
            <td>
                <input type="number" step="0.01" value="${i.price}" style="width:70px" onchange="patch(${i.id},{price:this.value})">
            </td>
            <td>
                <input type="number" value="${i.stock}" style="width:60px" onchange="patch(${i.id},{stock:this.value})">
            </td>
            <td>
                <button onclick="del(${i.id})">Delete</button>
            </td>
        </tr>`).join('')}

const addItem = async() =>{
    const b={
        price:document.getElementById('price').value||0,
        stock:document.getElementById('stock').value||0
    };

    const barcode = document.getElementById('barcode').value
    if(barcode.value){
        b.barcode=barcode.value
    }else {
        b.product_name=document.getElementById('name').value
    };

    if(await api('/inventory',json('POST',b)))
        load()
    }
async function patch(id,b){
    await api('/inventory/'+id,json('PATCH',b));
    load()
}
async function del(id){
    await api('/inventory/'+id,{method:'DELETE'});
    load()
}
async function search(){
    const r=await api('/lookup/search?name='+encodeURIComponent(q.value));
    if(!r){
        return
    }

    results.innerHTML=r.map(p=>`
        <li>
            ${p.product_name}
            (${p.brands}) - 
            ${p.barcode}
            <button onclick="barcode.value='${p.barcode}'">Use barcode</button>
        </li>`).join('')
}

load();