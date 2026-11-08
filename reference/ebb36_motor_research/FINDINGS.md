# Stock AD5M extruder connector - conversion-guide evidence

Checked November 3, 2026, after the user specifically asked about ChaoticWeaponry and Sedmenti.

## Practical conclusion

Do not repin the stock motor connector by default. The guides support an expectation that its existing adjacent coil pairs are suitable for an EBB36, but this remains a guide-based inference rather than a verified factory stock-motor pinout or a measurement of the user's cable.

## ChaoticWeaponry

- [Toolhead instructions](https://github.com/ChaoticWeaponry/AD5M_HardwareReplacement/blob/main/Toolhead/readme.md) retain the original extruder. Assembly step 10 says to plug in the extruder motor, hotend fan and thermistor connections; no motor-cable pin-swap step is specified.
- [Front connector drawing](https://github.com/ChaoticWeaponry/AD5M_HardwareReplacement/blob/main/Toolhead/Photos/toolheadconnectors.jpg) explicitly labels the custom extruder socket **A+, A-, B+, B-**, looking at its opening/pins with the key as pictured. Each winding occupies two adjacent contacts.
- This is a custom extension socket on a modified Mellow SB2040 Pro Max V3 installation, not a Flashforge factory stock-motor drawing. Do not copy its board pad positions onto the EBB36. The useful evidence is adjacent coil grouping plus the instruction to plug in the retained motor.
- [SB2040 board drawing](https://github.com/ChaoticWeaponry/AD5M_HardwareReplacement/blob/main/Toolhead/Photos/sb2040-pinout-diagram.jpg) labels its board pads separately. Board-pad order and socket-front order are different views/interfaces.

## Sedmenti

- [Guide](https://github.com/sedmenti/FlashForge_A5M_raspberry/blob/main/README.md) uses an EBB36 V1.2 without MAX31865 and retains the head components. No extruder motor repinning instruction or factory motor coil/color table appears in the README.
- Its explicit instruction to reverse JST poles occurs in the fan section and concerns fans adapted to the SKR Pico. It is not a motor instruction.
- Head photos were inspected, including `head_ph.jpg`, `head_pph.jpg`, and `headcap_inner.jpg`. They do not establish an unambiguous stock motor cavity-to-coil mapping.

## Comparison with BTT

BTT's EBB36 V1.2 schematic lists P11 motor contacts 1=A2, 2=A1, 3=B1, 4=B2. Thus contacts 1/2 form one winding and 3/4 the other, consistent with the adjacent-pair arrangement shown in ChaoticWeaponry's custom socket drawing. Coil polarity/direction is a separate commissioning issue.

The guides do not document a required stock motor pin swap. If actual lead order or motor identity differs, an unpowered resistance check establishes the pairs. Do not treat absence of a repinning instruction as a manufacturer guarantee.
