@page
def s5():
    return step_page('C · build', CUR, 5, 'Caps on all 18 servos', 'Same as step 1, on every servo. The bearing pocket is on the outside of the cap. The picture shows where the 18 end up.',
                     ['18 centred servos (dots up)', '18 **+2** caps (plate 10 + the one from plate 1)', '18 623ZZ bearings'],
                     ['Press a bearing into each cap\'s round pocket, flush with the face. Flat surface, steady thumb pressure.',
                      'Push the servo lead into the servo\'s rubber strain relief so it exits straight down. The cap notch is its only way out.',
                      'Slide the cap over the bottom of the servo, lead through the notch. Keep the shaft still.',
                      'Sort them: 6 go in the base (coxa), 12 go in the femur frames.'],
                     check=['Each bearing spins freely with a fingertip.', 'No cap turns on its servo. A loose one gets a wrap of tape on the servo.'],
                     img='s05', badge='×18', progress='s05_p', plabel='where they go')


@page
def s6():
    return step_page('C · build', CUR, 6, 'Coxa servos into the base', 'Base upside down to fit them: shafts point at the floor, caps up. Turn it back over and it looks like the picture.',
                     ['Base (16 inserts in)', '6 capped servos', '12× M3×6 + 12 washers'],
                     ['Turn the base over. Push each servo up through its pocket from below, cap first, until the tabs sit flat on the base.',
                      'Lead toward the middle of the base, not toward the leg.',
                      '**Outer tabs** (toward the leg): M3×6 + washer into the inserts. The inner tabs wait for step 7.',
                      'Turn the base right way up. Six caps on top, six shafts underneath.'],
                     check=['All six shafts face down, centred in their pockets. No servo rocks on its outer tab.'],
                     img='8:s06b', badge='×6', progress='s06_p',
                     wires=['The 6 coxa leads lie on top of the base, pointing at the centre. Coil the plugs loosely there.',
                            'They stay on top from now on: the electronics plate (step 13) goes over them and they come up through its windows.'])


@page
def s7():
    return step_page('C · build', CUR, 7, 'Bottom stiffeners, battery mount, switch', 'Underside. The stiffeners clamp the inner servo tabs and carry the battery. Structural: don\'t skip them.',
                     ['Bottom stiffeners, battery mount', '16× M3×10', 'Battery, Velcro strap', 'Fuse, switch, 2 zip ties'],
                     ['Base upside down again. Battery mount under the middle: its 4 corner ears go between the base and the stiffeners.',
                      'Stiffeners over the inner servo tabs and the ears.',
                      '**12× M3×10** through the counterbores, stiffener and tab into the base. They self-tap: snug only.',
                      '**4× M3×10** through the stiffener corners and the battery ears.',
                      'Battery in, Velcro strap through the slots. Leave it **unplugged**.'],
                     check=['Press on each coxa servo: nothing wobbles. The battery mount doesn\'t rattle.'], img='8:s07', progress='s07_p',
                     wires=['Zip-tie the **fuse and switch** to the side of the battery mount now, switch facing out where a finger reaches it. This is the last time the underside is this open.',
                            'Feed the switch\'s **output lead** (the one that will go to the Wagos) up through the gap beside the battery mount to the top of the base. Leave the battery\'s own XT60 underneath.',
                            'Balance lead: tuck it where the LiPo alarm can clip on from below.'])


@page
def s8():
    return step_page('C · build', CUR, 8, 'Coxa joints', 'The first joint of each leg. The servo is fixed in the base; the bracket swings. One leg shown; the progress picture has all six.',
                     ['Per leg: bracket A **coxa**, bracket B, 1 horn + its screws', '2× M3×8, 1× M3×10 (axle)'],
                     [ALU + ' **Target: B points straight out from the body.**',
                      'Bracket A over the top, its foot under the cap.',
                      'A to B: **2× M3×8** through B into A\'s inserts. Axle: **M3×10** up through A\'s foot into the bearing.',
                      'Swing the bracket gently to both ends of its travel (about 35° each way).'],
                     check=['All six coxa brackets point straight out. Smooth swing, no click, nothing pinched.'],
                     careful=['Don\'t turn the servo shaft to line the holes up. Turn the horn on the spline instead.'],
                     img='8:s08', badge='×6', progress='s08_p',
                     wires=['The coxa lead must not sit under bracket A\'s foot. Route it inward first, then check at both ends of the swing that A doesn\'t touch it.'])


@page
def s9():
    return step_page('C · build', CUR, 9, 'Femur frames', 'Built off the robot. Each femur carries two servos: femur servo (body end) and tibia servo (knee end).',
                     ['Per leg: 1 femur (2 inserts in), 2 capped servos', '6× M3×8, 2× M3×6', '1× 30 cm extension, 2 zip ties'],
                     ['Drop both servos in, cap first, from the insert face. The tabs rest on the frame.',
                      'Both output shafts on the **same side**.',
                      'The two knee-end holes have inserts: **M3×6**. The other six self-tap: **M3×8**.',
                      'Make all six frames identical. Lay them side by side: same side shafts, same side caps.'],
                     check=['Both shafts on one side, both caps poking out the other. All six frames match.'],
                     img='8:s09', badge='×6', progress='s09_p_p', plabel='all six, in place',
                     wires=['Plug the **30 cm extension** onto the tibia servo lead now and tape the joint.',
                            'Run both leads along the frame to the body end and zip-tie them to the rail (2 ties). The armour (step 12) covers the rails, so the leads go in first.'])


@page
def s10():
    return step_page('C · build', CUR, 10, 'Femur joints', 'The femur frame hangs off the coxa bracket. This time the servo body swings, not the bracket.',
                     ['Per leg: bracket A femur/tibia, bracket B, 1 horn + screws, a femur frame', '7× M3×10'],
                     ['Hold the femur frame **level**, sticking straight out. ' + ALU,
                      'Bracket A round the servo: foot under the cap, **2× M3×10** through B into A, **M3×10** axle.',
                      'Bolt this A back-to-back onto the coxa A: **4× M3×10** from inside the coxa bracket. The heads sink into its counterbores.',
                      'Lift the femur to the top of its range and back down. Nothing should pull.'],
                     check=['With the servos still centred, every femur sticks straight out and level.'], img='8:s10', badge='×6', progress='s10_p',
                     wires=['The leg\'s two leads now cross the coxa joint. Leave a **finger-sized loop** over the joint (coxa swings ±35°, femur −80 … +85°).',
                            'Then run them over the coxa bracket into the body, toward the centre of the base, next to the coxa lead.'])


@page
def s11():
    return step_page('C · build', CUR, 11, 'Tibia joints and grip feet', 'Last joint, then grip tape on the tip. The grip tape is the foot.',
                     ['Per leg: bracket A femur/tibia, bracket B, 1 horn + screws, 1 tibia', '7× M3×10, a strip of grip tape'],
                     ['Same U round the knee servo, axle included. ' + ALU.split('. Then')[0] + '. **Target: tibia straight down while the femur is level.** Then the horn\'s 4 screws.',
                      'Tibia onto A\'s 4-hole face: **4× M3×10** through the tibia\'s counterbores (they self-tap into A).',
                      'Wrap grip tape round the bottom **25 mm** of the tip, overlap on the inner face, press hard, trim.'],
                     check=['Femur level, tibia straight down, tape tight with no loose edge.'], img='8:s11', badge='×6', progress='s11_p',
                     wires=['No lead crosses this joint (the tibia has no servo). Fold the tibia all the way in and check the tibia lead at the knee isn\'t pulled tight.'])


@page
def s12():
    return step_page('C · build', CUR, 12, 'Check the legs, fit the armour', 'Everything at centre first, then the armour. It\'s cosmetic: glue or tape, no screws.',
                     ['The robot from step 11', '12 femur plates, 6 shin plates', 'CA glue or double-sided tape'],
                     ['Look at it from the front and the side: **coxa straight out, femur level, tibia straight down**, on every leg.',
                      'One off by more than a few degrees: its 4 horn screws out, horn one tooth, screws back.',
                      'Femur plates: one each side rail, rib outward, cut corner toward the knee. Glue only where the plate touches.',
                      'Shin plates: outer face of each tibia, flush with the bend at the top.',
                      'Move each leg by hand through its walking range (not to the end stops): nothing rubs.'],
                     check=['All six legs match. Errors under 2° get trimmed in software later.'], img='8:s12', badge='×6', progress='s12_p',
                     wires=['The femur leads are under the plates from now on. Before any glue: tug each lead, swing each leg, and only then stick the plates down.'])


@page
def oneleg():
    def d(c):
        image(c, R + 'oneleg.png', 36, 52, 170, 230)
        fitdraw(c, leg_pose, 214, 62, 0.93)
        x, t = 36, 300
        txt(c, x, t, 'SERIAL MONITOR KEYS  ·  115200, "No line ending"', 'MonoSB', 7.6, ORA)
        table(c, x, t + 16, [('key', 60), ('does', 398)], [
            ('`1` `2` `3`', 'pick coxa / femur / tibia. That joint powers on at its HOME_US'),
            ('`+` `-`', 'jog the picked joint 10 µs'), ('`]` `[`', 'jog 50 µs'),
            ('`p`', 'print `int HOME_US[3] = {…};` to paste into the sketch'),
            ('`t`', 'test: each joint moves +15° and back, one at a time'),
            ('`h`', 'home: joints power on one by one, 400 ms apart'),
            ('`w`', 'walk in the air (ramps in over 1 s)'), ('`x`', 'everything off')], size=8.4)
        para(c, x, t + 196, 'Faster: lower `CYCLE_MS` (1200; not under ~500). Longer steps: raise `STRIDE` (40; up to ~100 on the full robot). Higher steps: `LIFT` (25).', 8.4, 458, col=MUTE)
    return step_page('C · build', CUR, 12, 'One-leg walk test', 'Optional, but it\'s the proof the leg works before the electronics go in. One leg on the bench controller.',
                     ['The bench controller from step 4', '`vanta_one_leg_s3` (or the Uno one)', 'One finished leg (on the robot is fine)'],
                     ['Plug its servos into **ch 15 coxa, ch 14 femur, ch 13 tibia**. Upload the sketch. Nothing moves at boot.',
                      'Type `1`. Jog until the leg points **straight out**. `2`: femur **level**. `3`: tibia **straight down**.',
                      'Type `p`. Paste the line it prints over line 13 of the sketch. Upload again.',
                      'Type `t`. Each joint should move the way the picture shows. One goes backwards: flip its number in `SIGN[3]`.',
                      'Type `h`, then `w`. The foot draws a loop in the air. `x` to stop.'],
                     check=['A smooth loop, no snap, no buzzing at rest. Then try another leg the same way.'],
                     careful=['Never `w` before step 3 here. With HOME_US still at 1500 the leg can fold into the body.'],
                     draw=d, kicker='STEP 12 · B')


@page
def s13():
    return step_page('D · electronics', CUR, 13, 'Electronics plate', 'Top stiffeners, the plate, then the boards on it. Read the wires box before you pick up a screw.',
                     ['Top stiffeners, electronics plate (4 inserts in the posts)', '2 PCA boards, SBEC, buck', '4× M3×6, 8× M2.5×6, 4 zip ties'],
                     ['Top stiffeners on: the 4 base columns go through their corner notches; the stiffeners rest on the coxa servos.',
                      'Gather all the leads (wires box), then lower the plate onto the columns: **4× M3×6** into the column inserts. It clamps the stiffeners.',
                      'PCA boards on the bosses, servo headers facing out. **Front board (camera end) = PCA #1, rear = PCA #2.** Label them with tape.',
                      'Zip-tie the buck to the rear slots, the SBEC to the front slots.'],
                     check=['Nothing touches the coxa caps when you turn a leg by its bracket. All 19 leads are above the plate.'], img='8:s13', progress='s13_p',
                     wires=['Before the plate goes down: feed **all 18 servo leads and the switch output lead** up through the plate\'s two long windows.',
                            'Once the plate is screwed on, the top of the base is sealed. A lead left underneath means taking the plate off again.'])


@page
def s14():
    return step_page('D · electronics', CUR, 14, 'Power, in the robot', 'The bench wiring moves in. Same connections, now on both boards. Finish and test it now: the Pi deck covers most of this.',
                     ['Everything from step 3', 'Zip ties'],
                     ['Switch output lead (from step 7) into the Wagos on the plate, beside the SBEC.',
                      'SBEC to **both** PCA green terminals (red V+, black GND).',
                      'Buck output waits for the Pi (step 16). Fan leads too (step 18).',
                      'Test: battery in, switch on, **6.0 V** at both PCA terminals, **5.1 V** at the buck output. Switch off, battery out.'],
                     careful=['Battery stays unplugged after the test until step 17.'], check=['Every Wago lever closed, every wire tugged. No bare copper showing.'],
                     draw=lambda c: fitdraw(c, lambda c: power(c, 0, 0, robot=True), 36, 56, 0.85))


@page
def s15():
    return step_page('D · electronics', CUR, 15, 'Servo leads to the boards', 'All 18 leads, routed and plugged. Right legs on PCA #1, left legs on PCA #2. The channel map is on the next page.',
                     ['18 servo leads (tibias on their extensions)', 'Zip ties'],
                     ['Lay the 6 coxa leads flat on the plate, toward their board.',
                      'Each leg\'s femur and tibia leads come in over the coxa bracket and join the coxa lead.',
                      'Plug each leg\'s three leads into three channels in a row: coxa, femur, tibia. **Brown wire to the board edge**, every time.',
                      'Zip-tie each leg\'s bundle to the plate edge, leaving the slack loop at the joint.',
                      'Swing every leg through its full range: nothing pulls, nothing rubs a cap.'],
                     check=['18 leads in, no two on one channel. Next page: check each one against the map.'],
                     img='8:s15', progress='s15_p',
                     wires=['Keep the leads out of the two long windows: the Pi deck\'s jumpers come down through the left one at step 16.'])


@page
def s15b():
    return step_page('D · electronics', CUR, 15, 'Channel map', 'Seen from the top, camera at the front. Each leg has three channels in a row.',
                     None,
                     ['Right legs (FR, MR, RR) on **PCA #1**, the front board. Left legs (FL, ML, RL) on **PCA #2**.',
                      'Front legs: ch 0, 1, 2. Middle: 3, 4, 5. Rear: 6, 7, 8. Always coxa, femur, tibia in that order.',
                      'Write the leg name on a bit of tape on each bundle. You\'ll thank yourself at step 17.'],
                     check=['Walk round the robot once more with this page: every bundle on the right board, right channels.'],
                     draw=lambda c: fitdraw(c, leads, 36 + 12, -70, 0.82), kicker='STEP 15 · B')


@page
def s16():
    def d(c):
        image(c, R8 + 's16.png', 36, 52, 458, 250)
        pi_wiring(c, 40, 318)
    return step_page('D · electronics', CUR, 16, 'Pi deck and camera', 'The deck sits on the four posts. No screws yet: the hull bolts through it in step 18.',
                     ['Pi deck, Pi 4 (SD card from step 17A in), camera + ribbon', '4× M2.5×6, 4× M2×8 + nuts', '8 jumpers (Pi → PCAs) + 4 (buck → Pi)'],
                     ['Pi on its bosses, USB ports to the back. Camera on the front wall, lens through the hole.',
                      'Ribbon into the Pi\'s camera port, **blue tab toward the USB ports**.',
                      'Jumpers onto the Pi pins first, exactly as the drawing. Then the other ends onto the PCAs, down through the left window.',
                      'Buck output to **pins 2, 4 (+)** and **6, 9 (−)**. Measure 5.1 V first.',
                      'Deck onto the posts. Lay the servo wires flat before the Pi goes over them.'],
                     check=['Ribbon not pinched, jumpers not tight, nothing hanging into the legs.'], draw=d,
                     wires=['Use jumpers long enough that the deck can **lift 5 cm** off the posts with everything plugged in. That\'s how you get at the PCAs later without unplugging anything.'])
