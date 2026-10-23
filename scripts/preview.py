"""Generate a self-contained browser UI fixture from the production HUD assets."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fixture() -> str:
    web = ROOT / "addon/web"
    return (
        """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Anki Live HUD · UI test fixture</title>
<style>"""
        + web.joinpath("hud.css").read_text(encoding="utf-8")
        + """
body {display:flex;justify-content:center;gap:30px;padding:30px!important;min-height:100vh}
#fixture-controls{width:260px;padding:20px;font:14px system-ui;line-height:1.6}
#fixture-controls button,#fixture-controls select{margin:5px;padding:8px;border-radius:6px}
#hud{width:304px;border:1px solid var(--border);border-radius:14px;align-self:flex-start}
</style>
<aside id="fixture-controls"><h2>HUD test fixture</h2>
<p>Synthetic data for frontend testing. The native add-on uses your Anki collection.</p>
<div id="ratings"><button onclick="rate(1)">Again</button><button onclick="rate(2)">Hard</button>
<button onclick="rate(3)">Good</button><button onclick="rate(4)">Easy</button></div>
<button onclick="undo()">Undo</button><button onclick="reset()">Reset</button>
<select aria-label="Theme" onchange="cfg.theme=this.value;render()">
<option>dark</option><option>light</option></select>
<label><input type="checkbox" onchange="cfg.compact=this.checked;render()"> Compact</label><br>
<label><input type="checkbox" checked onchange="cfg.animations=this.checked;render()">
 Animations</label>
</aside>
"""
        + web.joinpath("hud.html").read_text(encoding="utf-8")
        + "<script>"
        + web.joinpath("hud.js").read_text(encoding="utf-8")
        + """</script><script>
const cfg = {theme:'dark',animations:true,compact:false,show_distribution:true};
let history=[];
function stats(){
 const counts=[0,0,0,0]; history.forEach(x=>counts[x-1]++);
 const n=history.length, correct=n-counts[0];
 return {again:counts[0],hard:counts[1],good:counts[2],easy:counts[3],reviews:n,correct,
 accuracy:n?correct/n*100:null,unique_cards:Math.min(n,8),last_rating:history.at(-1)||null,
 remaining:Math.max(0,16-n+counts[0]),day:1,goal:10,
 progress:Math.min(100,n*10),deck:'Everyday English'};
}
function render(reason='sync'){AnkiLiveHUD.update({stats:stats(),config:cfg,reason});}
function rate(r){history.push(r);render('answer');}
function undo(){history.pop();render();}
function reset(){history=[];render();}
render();
</script></html>"""
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "test-results/preview.html")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(fixture(), encoding="utf-8")
    print(args.output)
