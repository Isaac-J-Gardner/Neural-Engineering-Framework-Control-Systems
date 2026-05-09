# Neural-Engineering-Framework-Control-Systems
Isaac Gardner - Year 3 Meng Electronic Engineering, University of Manchester
ID: 11312345

This is the repository for my third year individual project. Requirements.txt provides the list of libraries required to run all the scripts.

Cartpole.py is the custom simulation environment used for all the results provided in the final report, with environment variables given in section 3.4.2.

Cartpole_LQR simulated a classical LQR controller used to produce a baseline for results, shown in experiment 1 results.
Cartple_LQR_NEF simulates a LQR controller implemented in nengo and is used for experiments 1, and 2.
NEF_LQR + integral.py (great name, don't hate on it) simulates an LQR controller with an integral term implemeted as a queue, added on as an extra connection. This file is used in experiment 3.
Cartpole_PD_NEF is the decomposed cascaded PD controller using 2 ensembles, implementing the same LQR control law used in experiment 4.
Attenuation_exp5.py is the nengo simulation used to produce the results of experiment 5. 
metrics.py takes in 3 arrays (time, error, input_to_system) and provides the 7 metrics used in experiments 1, 2, and 3. the metrics calculated in experiment 4 used matrics.py with adjustments made to how error was defined.

Pong_NEAT.py, Pong_NEF.py, Pong_user.py, and Pong.py were created during the learning phase of this project, during the literature review to improve understanding and build experience creating custom pygame environments.
