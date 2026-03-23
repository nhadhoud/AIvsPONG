**Game features:**
- Pong on Adafruit CLUE 240×240 display at 60fps
- Player controls bottom paddle via accelerometer tilt
- AI controls top paddle via neural network
- Continuous deflection: ball angle based on hit position relative to paddle centre (offset × 0.8)
- Ball speed escalation: +0.04× per hit, capped at 2.0×, resets each point
- Two modes: training (AI learns) and play (frozen weights), switched via buttons A/B

**Neural network:**
- Feedforward [6, 9, 1] shape, 73 parameters
- 6 inputs: ball x, ball y, ball vx, ball vy, own paddle centre, opponent paddle centre
- 1 output: sigmoid, thresholded with dead zone (< 0.45 left, > 0.55 right, between = stay)
- Xavier initialisation (1/√fan_in per layer)
- Sigmoid activation with ±10 clamping

**Training:**
- Backpropagation with momentum (μ = 0.9, lr = 0.35)
- Per-frame supervised tracking at 70% strength when ball approaches
- Reward-based reinforcement replay on game events
- On hit: reward scales with rally length (0.65 to 2.0)
- On AI miss: punishment proportional to miss distance (-0.3 to -1.0)
- On opponent miss: reward proportional to opponent miss distance (0.3 to 1.3)
- Circular experience replay buffer: 30 entries, pre-allocated, no dynamic allocation
- Adaptive exploration noise: 0.20 at rally start, decays to 0.0 as history fills
- Weight clipping at ±3.0 with velocity reset to prevent saturation
- Reinforcement lr_scale capped at 1.0
- Online learning from human opponent (not self-play)

**Optimisations:**
- Flat weight arrays instead of nested lists
- Unrolled output layer computation
- Pre-computed reciprocals (INV_S = 1/240)
- Cached gradient products (slr_do, slr_dh)
- Inlined sigmoid derivative
- Circular buffer with index wrap instead of append/pop
- Plain float for output bias instead of single-element list
- Local variable aliasing in forward/train
- Integer button states instead of string comparison
- Module-level constants instead of instance attributes
- Removed redundant offset input (reduced 82 to 73 params)
- Direct display object access (b.circle not b.getShape())
- Pre-computed frame interval DT = 1/60
- Removed all dead code
- Learning flag skips all training in play mode

**Persistence:**
- NVM save/load: 299 bytes (7 header + 73 × 4 float bytes)
- Byte-by-byte read/write to work around CircuitPython buffer protocol limitation
- Magic byte 0xAB for validation, shape descriptor for mismatch detection
- Saves on mode switch from training to play
- Loads once at boot
- Persists across power cycles

**Shape selection:**
- NEAT algorithm on desktop to explore architectures
- Hardware benchmark tool (optimize_clue.py) tests candidate shapes against 16.67ms budget
- [6, 9, 1] selected as largest shape fitting within budget

**PC tools:**
- find_agent.py: pygame GUI training 20 agents in parallel with play-against-human mode
- pong_pc.py: exact CLUE replica with hardware monitoring panel (estimated RAM, NVM, timing)
- optimize_clue.py: on-device shape benchmarking

**Self-play problem:**
- Shared network self-play caused cooperative equilibrium (both paddles hit straight)
- Solved by training against human opponent
- Distance-based opponent miss reward provides asymmetric incentive to aim strategically
