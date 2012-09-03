//
//  CrimeAnnotation.m
//  Mansfield PD
//
//  Created by Trevor Bakker on 7/4/12.
//  Copyright (c) 2012 __MyCompanyName__. All rights reserved.
//

#import "CrimeAnnotation.h"

@implementation CrimeAnnotation
@synthesize coordinate;


- (id)initWithLocation:(CLLocationCoordinate2D)coord {
    self = [super init];
    if (self) {
        coordinate = coord;
    }
    return self;
}
@end