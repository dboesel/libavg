//
//  libavg - Media Playback Engine. 
//  Copyright (C) 2003-2006 Ulrich von Zadow
//
//  This library is free software; you can redistribute it and/or
//  modify it under the terms of the GNU Lesser General Public
//  License as published by the Free Software Foundation; either
//  version 2 of the License, or (at your option) any later version.
//
//  This library is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
//  Lesser General Public License for more details.
//
//  You should have received a copy of the GNU Lesser General Public
//  License along with this library; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//  Current versions can be found at www.libavg.de
//
//  Original author of this file is igor@c-base.org 
//

#include "DeDistort.h"

#include "../base/XMLHelper.h"

#include <iostream>
#include <math.h>

const double sqrt3 = sqrt(3.);

using namespace std;

namespace avg{

// This transformation is based on the undistort code found at 
// http://www.math.rutgers.edu/~ojanen/undistort/index.html. 
//   a lot of parameters enter here, some of which can be calculated/set manually, 
//   some of which need to be determined via an optimization procedure
//
//   * m_FilmOffset moves the optical axis back to the center of the image:
//   * m_FilmScale scales the ROI to standard coords
//   * m_pDistortionParams OPT see paper
//   * m_Angle corrects rotation of camera OPT
//   * m_DisplayScale convert back from standard coords to display
//   * m_DisplayOffset correct the offset of the display from the center of the table
//     

void writePoint(xmlTextWriterPtr writer, string sName, DPoint& Val)
{
    int rc;
    rc = xmlTextWriterStartElement(writer, BAD_CAST sName.c_str());
    writeAttribute(writer, "x", Val.x);
    writeAttribute(writer, "y", Val.y);
    rc = xmlTextWriterEndElement(writer);

}

DeDistort::DeDistort()
    : m_FilmOffset(0,0),
      m_FilmScale(1,1),
      m_Angle(0.0),
      m_TrapezoidFactor(0),
      m_DisplayOffset(0,0),
      m_DisplayScale(1,1)
{
    m_DistortionParams.push_back(0);
    m_DistortionParams.push_back(0);
    m_RescaleFactor = calc_rescale();
}

DeDistort::DeDistort(const DRect &ROI, const DPoint &CamExtents,
            const std::vector<double>& DistortionParams,
            double Angle, double TrapezoidFactor,
            const DPoint& DisplayOffset, const DPoint& DisplayScale)
      : m_DistortionParams(DistortionParams),
      m_Angle(Angle),
      m_TrapezoidFactor(TrapezoidFactor),
      m_DisplayOffset(DisplayOffset),
      m_DisplayScale(DisplayScale)
{
    double w = ROI.Width();
    double h = ROI.Height();
    m_FilmOffset = -CamExtents/2+DPoint(ROI.tl); 
    m_FilmScale = DPoint(2./w,2./h);
    m_RescaleFactor = calc_rescale();
}

DeDistort::DeDistort(const DPoint& FilmOffset, const DPoint& FilmScale, 
            const std::vector<double>& DistortionParams,
            double Angle, double TrapezoidFactor,
            const DPoint& DisplayOffset, const DPoint& DisplayScale)
    : m_FilmOffset(FilmOffset),
      m_FilmScale(FilmScale),
      m_DistortionParams(DistortionParams),
      m_Angle(Angle),
      m_TrapezoidFactor(TrapezoidFactor),
      m_DisplayOffset(DisplayOffset),
      m_DisplayScale(DisplayScale)
{
    m_RescaleFactor = calc_rescale();
}

DeDistort::~DeDistort()
{
}

void DeDistort::load(xmlNodePtr pParentNode)
{
    xmlNodePtr curXmlChild = pParentNode->xmlChildrenNode;
    while (curXmlChild) {
        const char * pNodeName = (const char *)curXmlChild->name;
        if (!strcmp(pNodeName, "cameradisplacement")) {
            m_FilmOffset.x = getRequiredDoubleAttr(curXmlChild, "x");
            m_FilmOffset.y = getRequiredDoubleAttr(curXmlChild, "y");
        } else if (!strcmp(pNodeName, "camerascale")) {
            m_FilmScale.x = getRequiredDoubleAttr(curXmlChild, "x");
            m_FilmScale.y = getRequiredDoubleAttr(curXmlChild, "y");
        } else if (!strcmp(pNodeName, "distortionparams")) {
            m_DistortionParams.push_back(getRequiredDoubleAttr(curXmlChild, "p2"));
            m_DistortionParams.push_back(getRequiredDoubleAttr(curXmlChild, "p3"));
        } else if (!strcmp(pNodeName, "trapezoid")) {
            m_TrapezoidFactor = getRequiredDoubleAttr(curXmlChild, "value");
        } else if (!strcmp(pNodeName, "angle")) {
            m_Angle = getRequiredDoubleAttr(curXmlChild, "value");
        } else if (!strcmp(pNodeName, "displaydisplacement")) {
            m_DisplayOffset.x = getRequiredDoubleAttr(curXmlChild, "x");
            m_DisplayOffset.y = getRequiredDoubleAttr(curXmlChild, "y");
        } else if (!strcmp(pNodeName, "displayscale")) {
            m_DisplayScale.x = getRequiredDoubleAttr(curXmlChild, "x");
            m_DisplayScale.y = getRequiredDoubleAttr(curXmlChild, "y");
        }
        curXmlChild = curXmlChild->next;
    }
    m_RescaleFactor = calc_rescale();
}

void DeDistort::save(xmlTextWriterPtr writer)
{
    int rc;
    rc = xmlTextWriterStartElement(writer, BAD_CAST "transform");
    writePoint(writer, "cameradisplacement", m_FilmOffset);
    writePoint(writer, "camerascale", m_FilmScale);
    rc = xmlTextWriterStartElement(writer, BAD_CAST "distortionparams");
    writeAttribute(writer, "p2", m_DistortionParams[0]);
    writeAttribute(writer, "p3", m_DistortionParams[1]);
    rc = xmlTextWriterEndElement(writer);
    writeSimpleXMLNode(writer, "trapezoid", m_TrapezoidFactor);
    writeSimpleXMLNode(writer, "angle", m_Angle);
    writePoint(writer, "displaydisplacement", m_DisplayOffset);
    writePoint(writer, "displayscale", m_DisplayScale);
    rc = xmlTextWriterEndElement(writer);
}

DPoint DeDistort::transformScreenToBlob(const DPoint &pt){
    return 
        scale(DPoint(1/m_DisplayScale.x, 1/m_DisplayScale.y),  //scale back to real display resolution
            translate(-m_DisplayOffset, //translate 0,0 to center of display
                pt
                )
            );
}

DPoint DeDistort::inverse_transform_point(const DPoint &pt)
{
//    return inverse_undistort(m_DistortionParams, pt);
    return translate(-m_FilmOffset,
            scale(DPoint(1./m_FilmScale.x, 1./m_FilmScale.y),
                inverse_undistort(m_DistortionParams,
                    scale(m_RescaleFactor,
                        rotate(-m_Angle,
                            inv_trapezoid(m_TrapezoidFactor,
                                scale(m_FilmScale,
                                    translate(m_FilmOffset,
                                        pt
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            );
}

DPoint DeDistort::transformBlobToScreen(const DPoint &pt){
    return 
        translate(m_DisplayOffset, //translate 0,0 to center of display
                scale(m_DisplayScale,  //scale back to real display resolution
                    pt
                    )
                );

}      
DPoint DeDistort::transform_point(const DPoint &pt)
{
    return
        translate(-m_FilmOffset,
                scale(DPoint(1./m_FilmScale.x, 1./m_FilmScale.y),
                    trapezoid(m_TrapezoidFactor,
                        rotate(m_Angle, //rotate
                            scale(1./m_RescaleFactor,
                                undistort(m_DistortionParams, //undistort;
                                    scale(m_FilmScale,  // scale to -1,-1,1,1
                                        translate(m_FilmOffset, // move optical axis to (0,0) 
                                            pt 
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                );
}

DPoint DeDistort::inv_trapezoid(const double trapezoid_factor, const DPoint &pt)
{
    //stretch x coord
    double yn = pt.y;
    return DPoint( 
            pt.x/(1+yn*trapezoid_factor),
            pt.y);
}

DPoint DeDistort::trapezoid(const double trapezoid_factor, const DPoint &pt)
{
    //stretch x coord
    double yn = pt.y;
    return DPoint( 
            //m_Center.x + ( pt.x - m_Center.x) * (1 + m_TrapezoidFactor * yn), 
            pt.x * (1 + yn*trapezoid_factor),
            pt.y);
}

//scale a point around the origin
DPoint DeDistort::scale(const double scale, const DPoint &pt){
    return DPoint(pt.x, pt.y)*scale;
}

DPoint DeDistort::scale(const DPoint &scales, const DPoint &pt){
    return DPoint(pt.x*scales.x, pt.y*scales.y);
}

//translate a point pt by the distance displacement
DPoint DeDistort::translate(const DPoint &displacement, const DPoint &pt){
    return pt + displacement;
}

//rotate a point counter-clockwise around the origin
DPoint DeDistort::rotate(double angle, const DPoint &pt){
    return DPoint( 
            cos(angle) * pt.x - sin(angle) * pt.y, 
            sin(angle) * pt.x + cos(angle) * pt.y
            );
}

double distort_map(const std::vector<double> &params, double r) {
    double S = 0;
    int counter = 3;
    std::vector<double>::const_iterator v;
    for(v=params.begin(); v!=params.end(); ++v){
        S += (*v) * pow(r, counter);
        ++counter;
    }
    return r+S;
}

double DeDistort::calc_rescale(){
    //make sure that the undistort transformation stays within the normalized box
    double scale = distort_map(m_DistortionParams, sqrt(2.0));
    return scale/sqrt(2.0);
}

//bool everythingZero(const std::vector<double> &params)
//{
//    for (int i=0; i<params.size(); ++i) {
//        if (fabs(params[i]) > 0.00001) {
//            return false;
//        }
//    }
//    return true;
//}
//

double inv_distort_map(const std::vector<double> &params, double r) {
        double r1,r2,r3,f1,f2;
        r1 = r;
        r2 = r+.001;
        f1 = distort_map(params, r1)-r;
        f2 = distort_map(params, r2)-r;
        while (fabs(f2) > 0.0001) {
            r3 = (r1*f2-r2*f1)/(f2-f1);
            r1 = r2;
            r2 = r3;
            f1 = f2;
            f2 = distort_map(params, r2)-r;
        }
        return r2;
}

#define EPSILON 0.00001
DPoint DeDistort::inverse_undistort(const std::vector<double> &params, const DPoint &pt) {
    if ( params.empty() ) {
        return pt;
    }
    DPoint pt_norm = pt; //no need to scale anymore?
    double r_d = sqrt(pt_norm.x*pt_norm.x + pt_norm.y*pt_norm.y);
    double S;
    if (r_d < EPSILON){
        S=0;
    } else {
        S = inv_distort_map(params, r_d)/r_d;
    }
    DPoint result = pt_norm*(S);
    //cerr<<"inv distort: "<< result <<endl;
    return result;
}

DPoint DeDistort::undistort(const std::vector<double> &params, const DPoint &pt) {
    std::vector<double>::const_iterator v = params.begin();
    if ( v == params.end() ) {
        return pt;
    }
    DPoint pt_norm = pt; //no need to scale anymore?
    double r_d = sqrt(pt_norm.x*pt_norm.x + pt_norm.y*pt_norm.y);
    double S;
    if (r_d < EPSILON){
        S=0;
    } else {
        S = distort_map(params, r_d)/r_d;
    }
    
    DPoint result = pt_norm*(S);
    //cerr<<"distort: "<< result <<endl;
    return result;
}
    
}
