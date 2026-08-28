"use client";
import {useState} from "react";

export default function PurchasePathPreview() {
  const [date, setDate] = useState("later");
  return <main style={{minHeight:"100vh",background:"#f6f1e7",color:"#233c3b",fontFamily:"Georgia, serif",padding:"clamp(24px, 7vw, 96px)"}}>
    <a href="/">← Back to project workspace</a>
    <p style={{marginTop:48}}>Afford / experimental purchase-path composition</p>
    <h1 style={{fontSize:"clamp(40px, 7vw, 90px)",maxWidth:900}}>A purchase has more than one good date.</h1>
    <p>Interactive test fixture using synthetic content. Not financial guidance or an approved product.</p>
    <fieldset style={{maxWidth:640,marginTop:40,padding:24}}><legend>Compare a timing scenario</legend>
      <label style={{display:"block",padding:12}}><input type="radio" name="date" checked={date === "sooner"} onChange={() => setDate("sooner")}/> Sooner</label>
      <label style={{display:"block",padding:12}}><input type="radio" name="date" checked={date === "later"} onChange={() => setDate("later")}/> Later</label>
    </fieldset>
    <p role="status" style={{fontSize:24,maxWidth:680}}>{date === "sooner" ? "Explore the flexibility you would give up before committing." : "Explore what waiting could preserve. Real numbers require agreed product rules."}</p>
  </main>;
}
