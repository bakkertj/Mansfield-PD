//
//  CrimeAnnotation.h
//  Mansfield PD
//
//  Created by Trevor Bakker on 7/4/12.
//  Copyright (c) 2012 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <MapKit/MapKit.h>


@interface CrimeAnnotation : NSObject <MKAnnotation> {
    CLLocationCoordinate2D coordinate;
    NSString *title;
    NSString *subtitle;

}
@property (nonatomic) CLLocationCoordinate2D coordinate;
@property (nonatomic) NSString *title;
@property (nonatomic) NSString *subtitle;
- (id)initWithLocation:(CLLocationCoordinate2D)coord;

// Other methods and properties.
@end