import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf
import os
name = os.path.basename(__file__).split(".py")[0]#name="prueba"
pdf = matplotlib.backends.backend_pdf.PdfPages(name+".pdf")
###############


from ablr.linear.posterior import posterior, prior
from ablr.linear.predictive import moments_predictive, predictive, log_evidence
#from mathematics import pdf, cdf
from ablr.linear.likelihood import likelihood
from ablr.linear.generative import linear_model, sinus_model
from ablr.linear.basisFunctions import identity_basis_function, phi, polynomial_basis_function
import numpy as np
import math
from scipy.stats import multivariate_normal as normal
# Training dataset sizes

np.random.seed(1)

N = 20
N_list = [0, 1, 2, 4,N]

beta = (1/0.2)**2
alpha = (5e-7) # Bishop usa alpha = 5e-3

# Data 
X =np.random.rand(N_list[-1],1)-0.5
t = sinus_model(X, 1/beta)

# Grilla
X_grilla = np.linspace(0, 1, 100).reshape(-1, 1)-0.5
y_grilla = np.linspace(-1.4, 1.4, 100).reshape(-1, 1)
y_true = sinus_model(X_grilla , 0)

fig = plt.figure()   
plt.plot(X_grilla, y_true, '--', color="black")
plt.plot(X,t,'.', color='black')
plt.xticks(fontsize=12) # rotation=90
plt.yticks(fontsize=12) # rotation=90
plt.title("Objective function")
pdf.savefig(fig)



prior_predictive_online = np.zeros((10,1))
prior_predictive_joint = np.zeros((10,1)) 
log_evidence_joint = np.zeros((10,1)) 
for d in range(10):#d=1    
    for i in range(N_list[-1]) :#i=10
        X_train = X[:i]
        t_train = t[:i]
        x_test = X[i]
        t_test = t[i]
        # Design matrix of training observations
        Phi_train =  polynomial_basis_function(X_train, np.array(range(d+1)) )
        Phi_test = polynomial_basis_function(x_test , np.array(range(d+1)))
        Phi_test = Phi_test.reshape((1,d+1))
        
        prior_predictive_online[d,0] += np.log(predictive(t_test, Phi_test, beta, alpha, t_train, Phi_train ))
        
    Phi =  polynomial_basis_function(X, np.array(range(d+1)) )
    prior_predictive_joint[d,0] = np.log(predictive(t, Phi, beta, alpha ))
    log_evidence_joint[d,0] = log_evidence(t, Phi, beta, alpha)
    
fig = plt.figure()   
plt.plot(prior_predictive_joint)
plt.plot(log_evidence_joint)
plt.plot(prior_predictive_online)    
plt.xticks(fontsize=12) # rotation=90
plt.yticks(fontsize=12) # rotation=90
plt.ylabel("Evidence (log scale)", fontsize=16 )
plt.xlabel("Complexity (log scale)", fontsize=16 )
plt.title("Evidence")
pdf.savefig(fig)


###############3
pdf.close()    
    
'''
for d in range(10):#d=3
    X_0 = X[:0]
    t_0 = t[:0]
    Phi_0 =  polynomial_basis_function(X_0, np.array(range(d+1)) )        
    Phi_ = polynomial_basis_function(0.25, np.array(range(d+1)) ).reshape((1,d+1))
    plt.plot(y_grilla, predictive(y_grilla, Phi_, beta, alpha, t_0, Phi_0 ))
plt.savefig("img/example2_prior_predictive_at05.pdf".format(d))
plt.close()    

for d in range(10):#d=1
    Phi =  polynomial_basis_function(X, np.array(range(d+1)) )        
    Phi_ = polynomial_basis_function(0.25, np.array(range(d+1)) ).reshape((1,d+1))
    plt.plot(y_grilla, predictive(y_grilla, Phi_, beta, alpha, t, Phi ))
plt.savefig("img/example2_posterior_predictive_at05.pdf".format(d))
plt.close()    


#
belief = np.zeros((len(y_grilla),len(X_grilla),10))
for d in range(10):#d=1
    Phi =  polynomial_basis_function(X, np.array(range(d+1)) )
    for ix in range(len(X_grilla)):
        xi = X_grilla[ix]
        Phi_x = polynomial_basis_function(xi, np.array(range(d+1)))
        Phi_x = Phi_x.reshape((1,d+1))
        belief[:,ix,d] =  predictive(y_grilla, Phi_x, beta, alpha, t, Phi)[::-1] 
        
max_diff = -np.inf; 
min_diff = np.inf; 
for d in range(10):
    if max_diff < np.max(belief[:,:,3]-belief[:,:,d]):
        max_diff = np.max(belief[:,:,3]-belief[:,:,d])
    if min_diff > np.min(belief[:,:,3]-belief[:,:,d]):
        min_diff = np.min(belief[:,:,3]-belief[:,:,d])
        
for d in range(10):
    if d != 3:
        Zpos = np.ma.masked_less(np.log(belief[:,:,3]/belief[:,:,d]), 0)
        Zneg = np.ma.masked_greater(np.log(belief[:,:,3]/belief[:,:,d]), 0)
        plt.imshow(Zpos,extent=[-0.5,0.5,-1.4,1.4],cmap='Greens')
        plt.imshow(Zneg,extent=[-0.5,0.5,-1.4,1.4],cmap='Reds_r')
        plt.plot(X_grilla, y_true, '--', color="black")
        plt.savefig("example2_posterior_predictive_difference_3_{}.pdf".format(d))
        plt.close()


belief_at_true = np.zeros((10,len(X_grilla)))
for d in range(10):
    Phi =  polynomial_basis_function(X, np.array(range(d+1)) )
    for ix in range(len(X_grilla)):
        xi = X_grilla[ix]
        Phi_x = polynomial_basis_function(xi, np.array(range(d+1)))
        Phi_x = Phi_x.reshape((1,d+1))
        belief_at_true[d,ix] = predictive(y_true[ix].ravel(), Phi_x, beta, alpha, t, Phi)
plt.axhline(y=0, color='r', linestyle='-')
for d in range(10):#d=3
    if d != 3:
        plt.plot(X_grilla,belief_at_true[3,:]-belief_at_true[d,:])


i=20
belief = np.zeros((len(y_grilla),len(X_grilla),10))
for d in range(10):#d=1
    Phi =  polynomial_basis_function(X[:i], np.array(range(d+1)) )
    for ix in range(len(X_grilla)):
        xi = X_grilla[ix]
        Phi_x = polynomial_basis_function(xi, np.array(range(d+1)))
        Phi_x = Phi_x.reshape((1,d+1))
        belief[:,ix,d] =  predictive(y_grilla, Phi_x, beta, alpha, t[:i], Phi)[::-1] 


plt.close()
plt.plot(X_grilla,belief[:,0,3])
plt.plot(X_grilla,belief[:,0,9])

plt.close()
plt.plot(X_grilla,belief[:,24,3])
plt.plot(X_grilla,belief[:,24,9])

plt.close()
plt.plot(X_grilla,belief[:,49,3])
plt.plot(X_grilla,belief[:,49,9])

plt.close()
plt.plot(X_grilla,belief[:,74,3])
plt.plot(X_grilla,belief[:,74,9])

plt.close()
plt.plot(X_grilla,belief[:,-1,3])
plt.plot(X_grilla,belief[:,-1,9])

'''
