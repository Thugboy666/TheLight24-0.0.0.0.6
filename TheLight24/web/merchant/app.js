const API = location.origin.replace(/\/merchant.*$/,''); // assume mounted at /merchant

async function createShop(){
  const owner = v("owner"), star=v("star"), country=v("country")||"IT";
  const r = await post("/ecom/merchant/shop/create", {owner, star_name:star, country});
  set("shop_out", JSON.stringify(r,null,2));
  if(r.ok){ setValue("shop_id", r.shop.shop_id); }
}

async function enableShop(){
  const shop_id = v("shop_id");
  await post("/ecom/merchant/shop/enable", {shop_id, enabled: true});
}

async function flags(){
  const shop_id = v("shop_id");
  await post("/ecom/merchant/shop/flags", {shop_id, b2c: by("f_b2c").checked, b2b: by("f_b2b").checked, cod: by("f_cod").checked});
}

async function addProduct(){
  const shop_id = v("shop_id");
  const sku = v("p_sku"), title=v("p_title"), description=v("p_desc");
  const stock_qty = v("p_stock");
  const b2c_json = v("p_b2c"), b2b_json=v("p_b2b");
  const tags_csv = v("p_tags");
  const img = by("p_img").files[0];

  const fd = new FormData();
  fd.append("shop_id", shop_id);
  fd.append("sku", sku);
  fd.append("title", title);
  fd.append("description", description);
  fd.append("stock_qty", stock_qty);
  fd.append("b2c_json", b2c_json);
  fd.append("b2b_json", b2b_json);
  fd.append("tags_csv", tags_csv);
  if(img) fd.append("image", img);

  const r = await fetch(API+"/ecom/merchant/product/add", {method:"POST", body:fd}).then(x=>x.json());
  set("prod_out", JSON.stringify(r,null,2));
}

async function createCoupon(){
  const code=v("c_code"), percent=v("c_percent"), min_amount=v("c_min"), audience=v("c_aud"), uses=v("c_uses");
  const shop_id=v("shop_id");
  const r = await post("/ecom/merchant/coupon/create", {code, percent, min_amount, shop_id, audience, uses});
  set("coup_out", JSON.stringify(r,null,2));
}

async function listCoupons(){
  const shop_id=v("shop_id");
  const r = await get("/ecom/merchant/coupons?shop_id="+encodeURIComponent(shop_id));
  set("coup_out", JSON.stringify(r,null,2));
}

function by(id){return document.getElementById(id)}
function v(id){return by(id).value}
function set(id, val){by(id).textContent = val}
function setValue(id, val){by(id).value = val}

async function post(path, data){
  const fd = new FormData();
  Object.entries(data).forEach(([k,v])=>fd.append(k, v));
  const r = await fetch(API+path, {method:"POST", body:fd}).then(x=>x.json());
  return r;
}
async function get(path){
  return await fetch(API+path).then(x=>x.json());
}
