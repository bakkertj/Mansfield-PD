//
//  FirstViewController.m
//  Mansfield PD
//
//  Created by Trevor Bakker on 7/4/12.
//  Copyright (c) 2012 __MyCompanyName__. All rights reserved.
//

#import "FirstViewController.h"
#import <MapKit/MapKit.h>
#import "CrimeAnnotation.h"


#define kBgQueue dispatch_get_global_queue( DISPATCH_QUEUE_PRIORITY_DEFAULT,0) 
#define kLatestKivaLoansURL [NSURL URLWithString: @"http://localhost:8080"] 


@implementation FirstViewController
@synthesize mapView;

- (void)didReceiveMemoryWarning
{
    [super didReceiveMemoryWarning];
    // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLoad
{
    [super viewDidLoad];
    dispatch_async(kBgQueue, ^{
        NSData* data = [NSData dataWithContentsOfURL: 
                        kLatestKivaLoansURL];
        [self performSelectorOnMainThread:@selector(fetchedData:) 
                               withObject:data waitUntilDone:YES];
    });
	// Do any additional setup after loading the view, typically from a nib.
}

- (void)viewDidUnload
{
    [self setMapView:nil];
    [super viewDidUnload];
    // Release any retained subviews of the main view.
    // e.g. self.myOutlet = nil;
}

- (void)viewWillAppear:(BOOL)animated
{
    CLLocationCoordinate2D zoomLocation;
    zoomLocation.latitude = 32.577222;
    zoomLocation.longitude = -97.126667;
    
    MKCoordinateRegion viewRegion = MKCoordinateRegionMakeWithDistance(zoomLocation, 0.5 * METERS_PER_MILE, 0.5 * METERS_PER_MILE);
    
    MKCoordinateRegion adjustedRegion = [mapView regionThatFits:viewRegion];
    
    [mapView setRegion:adjustedRegion animated:YES];

}

- (void)viewDidAppear:(BOOL)animated
{
    [super viewDidAppear:animated];
}

- (void)viewWillDisappear:(BOOL)animated
{
	[super viewWillDisappear:animated];
}

- (void)viewDidDisappear:(BOOL)animated
{
	[super viewDidDisappear:animated];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    // Return YES for supported orientations
    return (interfaceOrientation != UIInterfaceOrientationPortraitUpsideDown);
}


- (void)fetchedData:(NSData *)responseData {
    //parse out the json data
    NSError* error;
    NSArray* json = [NSJSONSerialization 
                          JSONObjectWithData:responseData 
                          
                          options:kNilOptions 
                          error:&error];
  
    
    int count = [json count];
    for( int i = 0; i < count; ++i )
    {
        NSDictionary *keyArray =  [json objectAtIndex:i];
        NSLog(@"Date: %@", [keyArray objectForKey:@"date"]);
        NSLog(@"Incident: %@", [keyArray objectForKey:@"incident"]);
        NSLog(@"Details: %@", [keyArray objectForKey:@"details"]);
        NSLog(@"Location: %@", [keyArray objectForKey:@"location"]);

    
        CLGeocoder * geocoder = [[CLGeocoder alloc] init];
        
        NSString * address = [keyArray objectForKey:@"location"];
        NSString * town = @"Mansfield, Tx 76063";
        
        [address stringByAppendingString:town];
        
        [geocoder geocodeAddressString:address
                     completionHandler:^(NSArray* placemarks, NSError* error){
                         for (CLPlacemark* aPlacemark in placemarks)
                         {
                             CLLocation *location = [aPlacemark location];
                             MKPointAnnotation *annotationPoint = [[MKPointAnnotation  alloc] init];
                             annotationPoint.coordinate = [location coordinate];
                             annotationPoint.title = [keyArray objectForKey:@"incident"];
                             annotationPoint.subtitle = [keyArray objectForKey:@"details"];
                             
                             [mapView addAnnotation:annotationPoint];

                         }
                     }];
    };
    
    CLLocationCoordinate2D annotationCoord;
    
    annotationCoord.latitude =   32.577222;
    annotationCoord.longitude = -97.126667;

    
    MKPointAnnotation *annotationPoint = [[MKPointAnnotation alloc] init];
    annotationPoint.coordinate = annotationCoord;
    annotationPoint.title = @"Mansfield";
    annotationPoint.subtitle = @"Center of Mansfield\nSecond Line";

    [mapView addAnnotation:annotationPoint];
    

    


    NSLog(@"Here");
}

@end
