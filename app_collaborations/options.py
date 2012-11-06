from django.utils.translation import ugettext as _

#=========================================================================
# HELPERS
#=========================================================================
def get_creative_fields(category=None):
    def __get_values(res, v):
        val = list(v)
        if isinstance(v[0], tuple):
            for el in val:
                res = res + ((el[0], el[1]),)
        else:
            res = res + ((v[0],v[1]),)

        return res


    res = ()
    for k,v in MAP_CATEGORY_FIELDS.items():
        if category != None and category != k:
            pass
        else:
            res = __get_values(res, v)

    return sorted(res)


#=========================================================================
# OPTIONS
#=========================================================================
MAP_CATEGORY_FIELDS = {
    ('AR', 'Architecture'): (
                        ('A1', _('Architecture')), 
                        ('A2', _('Landscape Design')), 
                        ('A3', _('Street Design')),
    ),

    ('BS', 'Business'): (
                        ('B1', _('Advertising')), 
                        ('B2', _('Branding')),
                        ('B3', _('Entrepreneurship')), 
    ),

    ('CY', 'Cinematography'): (
                        ('C1', _('Cinematography')), 
                        ('C2', _('Directing')),
                        ('C3', _('Film')), 
                        ('C4', _('Storyboarding')),
    ),

    ('CU', 'Culinary Arts'): (
                        ('U1', _('Cooking')),
                        ('U2', _('Bakering')),
                        ('U3', _('Food and Beverage')),
                        ('U4', _('Food Critic')),
                        ('U5', _('Food Instructor')),
                        ('U6', _('Food Styling')),
                        ('U7', _('Food Writing')),
    ),

    ('DS', 'Design'): (
                        ('D1', _('Automotive Design')), 
                        ('D2', _('Exhibition Design')), 
                        ('D3', _('Furniture Design')),
                        ('D4', _('Industrial Design')), 
                        ('D5', _('Interior Design')), 
                        ('D6', _('Light Design')), 
                        ('D7', _('Packaging')), 
    ),

    ('EN', 'Engineering'): (
                        ('E1', _('Engineering')), 
                        ('E2', _('Information Architecture')), 
                        ('E3', _('Industrial Design')), 
                        ('E4', _('Product Design')), 
    ),

    ('FH', 'Fashion'): ( 
                        ('F1', _('Fashion')), 
                        ('F2', _('Fashion Styling')),
                        ('F3', _('Jewelry Design')), 
                        ('F4', _('MakeUp Arts')), 
    ),

    ('FI', 'Fine Arts'): (
                        ('R1', _('Calligraphy')),
                        ('R2', _('Comics')),
                        ('R3', _('Drawing')),
                        ('R4', _('Illustration')),
                        ('R5', _('Mosaics')),
                        ('R6', _('Painting')),
                        ('R7', _('Sculpting')),
    ),

    ('GR', 'Graphics'): (
                        ('G1', _('Animation')), 
                        ('G2', _('Computer Animation')),
                        ('G3', _('Digital Art')),
                        ('G4', _('Graphic Design')),
                        ('G5', _('Icon Design')), 
                        ('G6', _('Motion Graphics')),
                        ('G7', _('Visual Effects')),
    ),

    ('IT', 'Information Technology'): (
                        ('I1', _('Mobile Programming')), 
                        ('I2', _('Programming')), 
                        ('I3', _('Software Engineering')), 
                        ('I4', _('User Interface Design')), 
                        ('I5', _('Videogame Design')), 
                        ('I6', _('Web Design')), 
                        ('I7', _('Web Development')),                         
    ),

    ('JU', 'Journalism'): (
                        ('J1', _('Journalism')), 
                        ('J2', _('Photojournalism')), 
                        ('J3', _('Photoreporting')), 
    ),

    ('MA', 'Manual Arts'): (
                        ('M1', _('Crafts')), 
                        ('M2', _('Graffiti')),
    ),

    ('PF', 'Performing Arts'): (
                        ('P1', _('Acting')), 
                        ('P2', _('Dancing')), 
                        ('P3', _('Music')), 
    ),

    ('PH', 'Photography'): (
                        ('H1', _('Digital Photography')), 
                        ('H2', _('Photography')), 
    ),

    ('WR', 'Writing'): (
                        ('W1', _('Character Design')),
                        ('W2', _('Copywriting')), 
                        ('W3', _('Illustration')), 
                        ('W4', _('Typography')),
                        ('W5', _('Writing')), 
    ),
}


CATEGORIES      = MAP_CATEGORY_FIELDS.keys()
CREATIVE_FIELDS = get_creative_fields()
