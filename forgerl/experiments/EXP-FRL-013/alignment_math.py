"""Reference scalar objectives and verifiable repair reward."""
import math

def dpo_loss(chosen,rejected,ref_chosen,ref_rejected,beta=.1):
    delta=beta*((chosen-rejected)-(ref_chosen-ref_rejected))
    return math.log1p(math.exp(-delta))

def grouped_advantages(rewards):
    mean=sum(rewards)/len(rewards); variance=sum((x-mean)**2 for x in rewards)/len(rewards)
    scale=math.sqrt(variance)+1e-8
    return [(x-mean)/scale for x in rewards]

def clipped_grpo_loss(logprobs,old_logprobs,rewards,clip=.2):
    advantages=grouped_advantages(rewards); terms=[]
    for new,old,advantage in zip(logprobs,old_logprobs,advantages):
        ratio=math.exp(new-old); clipped=min(max(ratio,1-clip),1+clip)
        terms.append(-min(ratio*advantage,clipped*advantage))
    return sum(terms)/len(terms)

def repair_reward(valid_action,test_passed,finished,steps):
    return float(test_passed)+.1*float(valid_action)+.1*float(finished)-.01*steps
