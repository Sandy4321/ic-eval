#!/usr/bin/env python
from heuristics import *
import argparse
from common_tools import *
from graph_tools import createRandomGraph
import numpy as np
from generate_seeds import generateSeedFiles
from math import log

parser = argparse.ArgumentParser()
parser.add_argument('-csv', type = str, #required,
                    default = 'input/datasets/Wiki-Vote_stripped.txt', help="Name of source csv file (if we generate a new Link Server" )
parser.add_argument('-samples', type = int, default = 5,
                     help = '-samples : number of samples of given seed set size. Default: 10')
parser.add_argument('-cores', type = int, default = 30,
                    help = '-cores : number of cores of to use. Default: 50')
parser.add_argument('-undirected', type = int, default = 0,
                    help = '-undirected : is the graph undirected')
parser.add_argument('-output', type = str, default = 'out')
parser.add_argument('-dataset', type = str, default = 'input/datasets/wiki')
parser.add_argument('-max_k', type = float, default = .01,
                    help = '-max_k : maximum value for k/n. Default: .5')
parser.add_argument('-min_k', type = float, default = .001,
                    help = '-min_k : minimum value for k/n. Default: .05')
parser.add_argument('-k_step', type = float, default = .001,
                    help = '-k_step : .05')
parser.add_argument('-prob_method', type = int, default = 3)
parser.add_argument('-tau_scale', type = float, default = 0.5,
                    help = '-tau_scale : scaling factor for tau. Default: 0.1')

def test_heuristics(dataset_name, min_k, max_k, k_step, nSamples, results_file, tau_scale, cores):
    n = LinkServerCP(dataset_name).getNumNodes()
    nBFS_theoretic = int(n *log(n, 2))
    f = open(results_file,'w')
    f.write('# Dataset: %s\n'%dataset_name)
    f.write('\t'.join('INFEST(%d,%d)'%(init_samples, iter_samples) for init_samples, iter_samples in \
                      infest_heuristics) + '\n')
    f.write('\t'.join('Vanilla(%d)'%(vanilla_samples) for vanilla_samples in vanilla_heuristics) + '\n')
    f.close()
    for k_frac in np.arange(min_k, max_k, k_step):
        print "k_frac = ", k_frac
        k = int(n * k_frac)
        seeds_fname = "%s-seeds-%d.cp"%(dataset_name, k)
        for i in xrange(nSamples):
            print "sample #",i
            print "Testing heuristics for dataset: ", dataset_name
            generateSeedFiles(k, k+1, 1, range(n), 1, dataset_name + "-seeds-")
            seeds=cp.load(open(seeds_fname,'r'))
            print "Running Vanilla with %d samples"%(nBFS_samples)
            true_value, num_cycles_full = 0, 0 
            true_value, num_cycles_full = runVanilla(dataset_name, seeds_fname, nBFS_samples, parameters.cores)            
            num_cycles_full = int(1. * nBFS_theoretic / nBFS_samples * num_cycles_full)
            infest_results = []
            print "Running INFEST based heuristics"
            for init_samples, iter_samples in infest_heuristics:
                print "INFEST(%d,%d)"%(init_samples, iter_samples)
                approx_estimate, num_cycles_approx = runApproxHeuristic(dataset_name, seeds_fname, tau_scale, parameters.cores,\
                                                 init_samples, iter_samples)
                infest_results.append((approx_estimate, num_cycles_approx))
            
            vanilla_results = []
            print "Running Vanilla based heuristics"
            for samples in vanilla_heuristics:
                seq_estimate, num_cycles_seq = runVanilla(dataset_name, seeds_fname, samples, parameters.cores)
                vanilla_results.append((seq_estimate, num_cycles_seq))
            
            removeFile(seeds_fname)
            f = open(results_file, 'a')
            f.write('%.5f\t%.4f\t%d\t'%(k_frac, true_value, num_cycles_full) + '\t'.join('%d\t%d'%results for results in infest_results) + '\t' + \
                    '\t'.join('%d\t%d'%results for results in vanilla_results) + '\n')
            f.close()
    

if __name__ == "__main__":
    
    parameters = parser.parse_args()
    
    dataset, csv, prob_method, min_k, max_k, k_step, nSamples, tau_scale = parameters.dataset, parameters.csv, parameters.prob_method, \
      parameters.min_k, parameters.max_k, parameters.k_step, parameters.samples, parameters.tau_scale
    results_dir = "experiments/results/heuristics/"

    global infest_heuristics
    global vanilla_heuristics
    global nBFS_samples
    
    synthetic_n = 1000
    synthetic_datasets = [('BarabasiAlbert', 2), ('Kronecker', 3), ('SmallWorld',4), ('ConfigurationModel',4)]
    real_datasets = [('WikiVote', 'input/datasets/Wiki-Vote_stripped.txt')]

    
    if parameters.prob_method == 2:
        prob_values = [.1,.01]
    if parameters.prob_method == 3:
        prob_values = [0, 1]
    
    nBFS_samples = 500
    
    ## setting heuristics parameters

    infest_heuristics = [(-1, -1), (-1, 10), (10,10)]
    vanilla_heuristics = [10, 20, 30, 40, 50]

    ## Debug
    #nSamples = 1
    #max_k = .0011
    ##
    
    results_file_pattern = results_dir + "%s-heuristics_comparison-min_k-%.3f-max_k-%.3f-nSamples-%d-prob_method-%d-tau_scale-%.3f"
    
    ## for dataset in synthetic_datasets[:1]:
    ##     csv_fname = 'input/datasets/random_graph.csv'
    ##     results_file = results_file_pattern %(dataset[0], min_k, max_k, nSamples, prob_method, tau_scale)
    ##     f =  open(results_file,'w')
    ##     f.write("# Prob method: %d\n"%prob_method)
    ##     f.close()
    ##     createRandomGraph(csv_fname, dataset[1], n = synthetic_n)
    ##     L = LinkServerCP(dataset[0], csv_fname, create_new=True, prob_method = parameters.prob_method, prob=prob_values, delim='\t')
    ##     test_heuristics(dataset[0], min_k, max_k, k_step, nSamples, results_file, parameters.tau_scale, parameters.cores)
    ##     removeFile('input/datasets/random_graph.csv')
    ##     removeFile(csv_fname)
    ##     ## cleanup
    ##     removeFile(dataset)
    
    for dataset in real_datasets:
        "Running tests for dataset:", dataset[0]
        results_file = results_file_pattern %(dataset[0], min_k, max_k, nSamples, prob_method, tau_scale)
        f =  open(results_file,'w')
        f.write("# Prob method: %d\n"%prob_method)
        f.close()

        L = LinkServerCP(dataset[0], dataset[1], create_new=True, prob_method = parameters.prob_method, prob=prob_values, delim='\t')
        test_heuristics(dataset[0], min_k, max_k, k_step, nSamples, results_file, parameters.tau_scale, parameters.cores)
        ## cleanup
        removeFile(dataset[0])

    
