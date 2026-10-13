# Rubber hose: working notes

What the style asks for, gathered on 2026-10-13 from written sources only (no
video could be watched), and how each point applies to the coin built by
`tools/pixel/build_peseta.py`. Sources are listed at the end. Where a rule is
my own reading rather than something a source states, it says so.

## Where the style comes from

- New York studios, 1920s. Bill Nolan rounded Felix the Cat and is credited
  with the style; Fleischer kept it longest (until about 1940); Disney and Ub
  Iwerks used a tamer, more mechanical variant for Oswald and Mickey.
- It was born of economy: newspaper cartoonists had to redraw a character
  thousands of times, so everything is circles, curves and few details.
- It faded after 1937 as studios chased lifelike anatomy. Revived by Cuphead
  (hand-drawn, inked, watercolour backgrounds, animated at 24 frames a second,
  human imperfections kept on purpose) and MOUSE: P.I. For Hire.
- Fleischer is the darker, stranger pole of it ("subversive and surrealist");
  that is the pole the owner wants: adult, old, slightly dark.

## Drawing

1. **Build from round shapes.** Head a circle, body a pear, no sharp angles.
   The coin already is one big circle; the hat, gloves and shoes are the only
   other masses and should stay round.
2. **Limbs are hoses.** Even width, no elbows or knees, one flowing curve.
   They may stretch. Never a kink, never two bends at once in a relaxed limb.
3. **Hands are gloves.** Three fingers and a thumb; the fingers are told apart
   by short lines, and three lines sit on the back of the hand. A glove reads
   as one white shape.
4. **Eyes are tall ovals with a pie slice cut from the pupil**, or plain
   dots. Mouths are big and rubbery. Brows float free of the eye.
5. **Line.** One pen of even weight throughout; a line that changes thickness
   from drawing to drawing makes the character boil. Keep detail low.
6. **Colour.** Flat blocks, greyscale or sepia. Shading is the exception, not
   the rule. (The owner's picture does shade softly; follow the picture.)
7. **A pose is a frame plucked from a cartoon.** One clear line of action,
   an exaggerated attitude, and never "twins": the two arms, or the two legs,
   doing the same thing in mirror image looks dead.

## Moving

8. **Bounce.** The style is animated to a beat; everything bobs. A walk is
   four positions per step — contact, down, passing, up — so eight per
   cycle, and the body drops after each contact and rises over the passing
   leg.
9. **Arcs.** Hands, feet and the body travel on curves, never straight lines.
10. **Squash and stretch, at constant volume.** What gets taller gets thinner.
11. **Anticipation.** A small move the opposite way before the main one: a
    crouch before a jump, a wind-up before a reach.
12. **Follow through and overlap.** Loose ends keep going after the body
    stops, and parts move at different rates: a hand trails its arm, a hat
    lags the head.
13. **Slow in, slow out.** More drawings near the ends of a move, fewer in the
    middle.
14. **Arms swing against the legs**, as pendulums that lag a little.
15. **Timing is character.** Lingering on the contact reads tired; a small
    up-and-down reads sneaky; a big one reads jaunty.

## The coin against these rules

State after the pass of 2026-10-13 that worked through the list below in
order. All of it was judged on still frames, not in motion.

| Rule | State |
|---|---|
| 2 hoses | One soft bend per limb; gloves and shoes turn to meet them. |
| 3 gloves | The picture's fist, plus an open hand and a pointing hand drawn to go with it (`draw_glove`). They are plainer than the picture's. |
| 5 line | Limbs and the two drawn gloves are one weight; turning pieces by odd angles still roughens their line a little. |
| 7 twins | Broken at rest: near fist on the hip with the elbow out, far arm hanging, far foot turned out. |
| 8 bounce | Walk has the four positions per step with the drop and rise. |
| 9 arcs | Hands rise at the ends of their swing; feet lift on a sine. |
| 10 squash | The coin squashes a little on each landing, crouch and breath and stretches on the way up, about its lowest point. It is scaled, not redrawn, by at most 5 %: at full size a row of pixels doubles or drops for a frame. |
| 11 anticipation | Cheer: crouch, hop, settle. Reach: a pull back first, then a stretch a hair too far, then the return. |
| 12 overlap | Arms trail their swing. The hat is its own piece (`split_hat`) and follows the coin a frame late; it leaves the head at the top of the hop and streams behind in the run. The strip of coin under it is a smear of the metal below the brim, good only for the sliver that shows. |
| 13 slow in/out | In the foot's swing only. |
| 15 timing | A walk and a separate run (shorter contact, time in the air, arms pumping). |

Sleep is now sitting, legs out, hands in the lap, hat over the eyes; not
lying down, which would need the coin drawn flat.

## Still open

1. Look at all of it moving in the game and fix what stills hid.
2. The drawn gloves against the picture's fist: match its shading.
3. Squash and stretch by redrawing rather than scaling, if the doubled row
   shows.
4. Slow in and out on arms and on the reach.
5. Shrug, stretch and watch still borrow other strips.

## Sources

- Wikipedia, "Rubber hose animation" and "Twelve basic principles of
  animation" and "Cuphead" (development).
- RetroSupply, "Rubber hose cartoon tutorial".
- Search summaries on Richard Williams's contact method for walks and on
  Preston Blair's "Cartoon Animation" (the books themselves were not read).
- Earlier the same day: Derek Yu's pixel art tutorial and Pixel Parmesan on
  anti-aliasing.

Not obtained: any video; the Clip Studio article (page unavailable); a
proper tutorial on cartoon gloves.
