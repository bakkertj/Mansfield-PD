//
//  FirstViewController.h
//  Mansfield PD
//
//  Created by Trevor Bakker on 7/4/12.
//  Copyright (c) 2012 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <MapKit/MapKit.h>

#define METERS_PER_MILE 1609.344

@interface FirstViewController : UIViewController

@property (weak, nonatomic) IBOutlet MKMapView *mapView;

@end
