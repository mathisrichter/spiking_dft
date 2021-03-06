from brian2 import *
from brian2tools import *
import matplotlib

N = 120
v_rest = -70*mV
v_reset = v_rest
firing_threshold = -55*mV
time_scale = 8.0*ms
time_scale_input = 10.0*ms
refractory_period = 2.0*ms

eqs = '''
    dv/dt = (-v + v_rest + s)/time_scale: volt (unless refractory)
    ds/dt = -s/time_scale_input : volt
    '''

reset_eqs = '''
    v -= (firing_threshold - v_reset)
    s = 0.0 * mV
    '''


# 1D neural field
G = NeuronGroup(N, eqs, threshold='v>firing_threshold', reset=reset_eqs, refractory=refractory_period, method='exact')
G.v = v_rest
G.s = 0.0 * mV

exc = 1.0
inh = 0.4
width = 15.0

S = Synapses(G, G, 'w : volt', delay=3*ms, on_pre='s+=w')
S.connect()
S.w = '(exc * exp(-(i-j)**2/(2*(width**2))) - inh * exp(-(i-j)**2/(2*((2 * width)**2)))) * mV'


# 1D neural field without interaction
# (this is only used to show the effect of recurrent connections)
G1 = NeuronGroup(N, eqs, threshold='v>firing_threshold', reset=reset_eqs, refractory=refractory_period, method='exact')
G1.v = v_rest
G1.s = 0.0 * mV


# input
input_center1 = 40.0
input_center2 = 100.0
input_strength = 2000.0
PG = PoissonGroup(N, 'input_strength * (exp(-(input_center1-i)**2/(2*6.0**2)) + exp(-(input_center2-i)**2/(2*6.0**2)))* Hz')
SP = Synapses(PG, G, on_pre='s+=1.0 * mV')
SP.connect(j='i')
SP1 = Synapses(PG, G1, on_pre='s+=1.0 * mV')
SP1.connect(j='i')


# monitors
MP = SpikeMonitor(PG)
M = SpikeMonitor(G)
M1 = SpikeMonitor(G1)
MS = StateMonitor(G, variables='v', record=True)
MR = PopulationRateMonitor(G)
MR1 = PopulationRateMonitor(G1)

net = Network(collect())  # automatically include the above monitors

l = 2 # number of neurons in a subgroup
number_of_subgroups = math.floor(N/l)
pop_rate_monitors = [ PopulationRateMonitor(G[n*l:(n*l)+l]) for n in range(0, number_of_subgroups) ]
net.add(pop_rate_monitors) # manually add these monitors (they are not automatically added because they are in a list


# simulation
runtime = 2*second

net.run(runtime/3.)
input_center1 = 50.
input_center2 = 90.
net.run(runtime/3.)
input_center1 = 62.
input_center2 = 78.
net.run(runtime/3.)


# plotting
figure()
suptitle('Poisson input to the field')
plot(MP.t/ms, MP.i, '.k')
xlabel('Time (ms)')
ylabel('Input index')
xlim(0,runtime/ms)
ylim(0,N)

figure()
suptitle('Spikes of the field')
plot(M.t/ms, M.i, '.k')
xlabel('Time (ms)')
ylabel('Neuron index')
xlim(0,runtime/ms)
ylim(0,N)

figure()
suptitle('Spikes of the field (without interaction)')
plot(M1.t/ms, M1.i, '.r')
xlabel('Time (ms)')
ylabel('Neuron index')
xlim(0,runtime/ms)
ylim(0,N)

figure()
suptitle('Spike rate of the field')
plot(MR.t/ms, MR.smooth_rate(width=50*ms), 'k', label='interaction')
plot(MR1.t/ms, MR1.smooth_rate(width=50*ms), 'r', label='no interaction')
xlabel('Time (ms)')
ylabel('Firing rate (spikes/s)')
legend()


figure()
suptitle('Spike rate of the field (Hz)')
pop_spikerates = np.vstack([np.array(monitor.smooth_rate(width=50*ms)) for monitor in pop_rate_monitors])
im = pcolormesh(pop_spikerates)
colorbar(im)
xlabel('Time (ms)')
ylabel('Neuron index')
legend()

figure()
suptitle('Membrane potential of all field neurons (with interaction)')
brian_plot(MS)

figure()
suptitle('Kernel of the field (with interaction)')
brian_plot(S.w)
show()
