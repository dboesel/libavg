//
//  libavg - Media Playback Engine. 
//  Copyright (C) 2003-2011 Ulrich von Zadow
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

#include "CircleNode.h"

#include "NodeDefinition.h"

#include "../base/Exception.h"

#include <iostream>
#include <sstream>

using namespace std;

namespace avg {

NodeDefinition CircleNode::createDefinition()
{
    return NodeDefinition("circle", Node::buildNode<CircleNode>)
        .extendDefinition(FilledVectorNode::createDefinition())
        .addArg(Arg<DPoint>("pos", DPoint(0,0), false, offsetof(CircleNode, m_Pos)))
        .addArg(Arg<double>("r", 1, false, offsetof(CircleNode, m_Radius)))
        .addArg(Arg<double>("texcoord1", 0, false, offsetof(CircleNode, m_TC1)))
        .addArg(Arg<double>("texcoord2", 1, false, offsetof(CircleNode, m_TC2)))
        ;
}

CircleNode::CircleNode(const ArgList& args)
    : FilledVectorNode(args)
{
    args.setMembers(this);
}

CircleNode::~CircleNode()
{
}

const DPoint& CircleNode::getPos() const 
{
    return m_Pos;
}

void CircleNode::setPos(const DPoint& pt) 
{
    m_Pos = pt;
    setDrawNeeded();
}

double CircleNode::getR() const 
{
    return m_Radius;
}

void CircleNode::setR(double r) 
{
    if (int(r) <= 0) {
        throw Exception(AVG_ERR_OUT_OF_RANGE, "Circle radius must be a positive number.");
    }
    m_Radius = r;
    setDrawNeeded();
}

double CircleNode::getTexCoord1() const
{
    return m_TC1;
}

void CircleNode::setTexCoord1(double tc)
{
    m_TC1 = tc;
    setDrawNeeded();
}

double CircleNode::getTexCoord2() const
{
    return m_TC2;
}

void CircleNode::setTexCoord2(double tc)
{
    m_TC2 = tc;
    setDrawNeeded();
}

void CircleNode::getElementsByPos(const DPoint& pos, vector<NodeWeakPtr>& pElements)
{
    if (calcDist(pos, m_Pos) <= m_Radius && reactsToMouseEvents()) {
        pElements.push_back(shared_from_this());
    }
}

void CircleNode::calcVertexes(VertexArrayPtr& pVertexArray, Pixel32 color)
{
    // TODO: This gets called whenever the circle position changes and is quite 
    // expensive. Should be optimized away.
    DPoint firstPt1 = getCirclePt(0, m_Radius+getStrokeWidth()/2)+m_Pos;
    DPoint firstPt2 = getCirclePt(0, m_Radius-getStrokeWidth()/2)+m_Pos;
    int curVertex = 0;
    pVertexArray->appendPos(firstPt1, DPoint(m_TC1, 0), color);
    pVertexArray->appendPos(firstPt2, DPoint(m_TC1, 1), color);
    vector<DPoint> innerCircle;
    getEigthCirclePoints(innerCircle, m_Radius-getStrokeWidth()/2);
    vector<DPoint> outerCircle;
    getEigthCirclePoints(outerCircle, m_Radius+getStrokeWidth()/2);
    
    typedef vector<DPoint>::iterator DPointIt;
    typedef vector<DPoint>::reverse_iterator DPointRIt;
    int i = 0;
    for (DPointIt iit = innerCircle.begin()+1, oit = outerCircle.begin()+1; 
            iit != innerCircle.end(); ++iit, ++oit)
    {
        appendCirclePoint(pVertexArray, *iit, *oit, color, i, curVertex);
    }
    for (DPointRIt iit = innerCircle.rbegin()+1, oit = outerCircle.rbegin()+1; 
            iit != innerCircle.rend(); ++iit, ++oit)
    {
        DPoint iPt = DPoint(-iit->y, -iit->x);
        DPoint oPt = DPoint(-oit->y, -oit->x);
        appendCirclePoint(pVertexArray, iPt, oPt, color, i, curVertex);
    }
    for (DPointIt iit = innerCircle.begin()+1, oit = outerCircle.begin()+1; 
            iit != innerCircle.end(); ++iit, ++oit)
    {
        DPoint iPt = DPoint(-iit->y, iit->x);
        DPoint oPt = DPoint(-oit->y, oit->x);
        appendCirclePoint(pVertexArray, iPt, oPt, color, i, curVertex);
    }
    for (DPointRIt iit = innerCircle.rbegin()+1, oit = outerCircle.rbegin()+1; 
            iit !=innerCircle.rend(); ++iit, ++oit)
    {
        DPoint iPt = DPoint(iit->x, -iit->y);
        DPoint oPt = DPoint(oit->x, -oit->y);
        appendCirclePoint(pVertexArray, iPt, oPt, color, i, curVertex);
    }
    for (DPointIt iit = innerCircle.begin()+1, oit = outerCircle.begin()+1; 
            iit != innerCircle.end(); ++iit, ++oit)
    {
        DPoint iPt = DPoint(-iit->x, -iit->y);
        DPoint oPt = DPoint(-oit->x, -oit->y);
        appendCirclePoint(pVertexArray, iPt, oPt, color, i, curVertex);
    }
    for (DPointRIt iit = innerCircle.rbegin()+1, oit = outerCircle.rbegin()+1; 
            iit != innerCircle.rend(); ++iit, ++oit)
    {
        DPoint iPt = DPoint(iit->y, iit->x);
        DPoint oPt = DPoint(oit->y, oit->x);
        appendCirclePoint(pVertexArray, iPt, oPt, color, i, curVertex);
    }
    for (DPointIt iit = innerCircle.begin()+1, oit = outerCircle.begin()+1; 
            iit != innerCircle.end(); ++iit, ++oit)
    {
        DPoint iPt = DPoint(iit->y, -iit->x);
        DPoint oPt = DPoint(oit->y, -oit->x);
        appendCirclePoint(pVertexArray, iPt, oPt, color, i, curVertex);
    }
    for (DPointRIt iit = innerCircle.rbegin()+1, oit = outerCircle.rbegin()+1; 
            iit != innerCircle.rend(); ++iit, ++oit)
    {
        DPoint iPt = DPoint(-iit->x, iit->y);
        DPoint oPt = DPoint(-oit->x, oit->y);
        appendCirclePoint(pVertexArray, iPt, oPt, color, i, curVertex);
    }
}

void CircleNode::calcFillVertexes(VertexArrayPtr& pVertexArray, Pixel32 color)
{
    DPoint minPt = m_Pos-DPoint(m_Radius, m_Radius);
    DPoint maxPt = m_Pos+DPoint(m_Radius, m_Radius);
    DPoint centerTexCoord = calcFillTexCoord(m_Pos, minPt, maxPt);
    pVertexArray->appendPos(m_Pos, centerTexCoord, color);
    int curVertex = 1;
    DPoint firstPt = getCirclePt(0, m_Radius)+m_Pos;
    DPoint firstTexCoord = calcFillTexCoord(firstPt, minPt, maxPt);
    pVertexArray->appendPos(firstPt, firstTexCoord, color);
    vector<DPoint> circlePoints;
    getEigthCirclePoints(circlePoints, m_Radius);

    for (vector<DPoint>::iterator it = circlePoints.begin()+1; it != circlePoints.end();
            ++it)
    {
        DPoint curPt = *it+m_Pos;
        appendFillCirclePoint(pVertexArray, curPt, minPt, maxPt, color, curVertex);
    }
    for (vector<DPoint>::reverse_iterator it = circlePoints.rbegin()+1; 
            it != circlePoints.rend(); ++it)
    {
        DPoint curPt = DPoint(-it->y, -it->x)+m_Pos;
        appendFillCirclePoint(pVertexArray, curPt, minPt, maxPt, color, curVertex);
    }
    for (vector<DPoint>::iterator it = circlePoints.begin()+1; it != circlePoints.end();
            ++it)
    {
        DPoint curPt = DPoint(-it->y, it->x)+m_Pos;
        appendFillCirclePoint(pVertexArray, curPt, minPt, maxPt, color, curVertex);
    }
    for (vector<DPoint>::reverse_iterator it = circlePoints.rbegin()+1; 
            it != circlePoints.rend(); ++it)
    {
        DPoint curPt = DPoint(it->x, -it->y)+m_Pos;
        appendFillCirclePoint(pVertexArray, curPt, minPt, maxPt, color, curVertex);
    }
    for (vector<DPoint>::iterator it = circlePoints.begin()+1; it != circlePoints.end();
            ++it)
    {
        DPoint curPt = DPoint(-it->x, -it->y)+m_Pos;
        appendFillCirclePoint(pVertexArray, curPt, minPt, maxPt, color, curVertex);
    }
    for (vector<DPoint>::reverse_iterator it = circlePoints.rbegin()+1;
            it != circlePoints.rend(); ++it)
    {
        DPoint curPt = DPoint(it->y, it->x)+m_Pos;
        appendFillCirclePoint(pVertexArray, curPt, minPt, maxPt, color, curVertex);
    }
    for (vector<DPoint>::iterator it = circlePoints.begin()+1; it != circlePoints.end();
            ++it)
    {
        DPoint curPt = DPoint(it->y, -it->x)+m_Pos;
        appendFillCirclePoint(pVertexArray, curPt, minPt, maxPt, color, curVertex);
    }
    for (vector<DPoint>::reverse_iterator it = circlePoints.rbegin()+1;
            it != circlePoints.rend(); ++it)
    {
        DPoint curPt = DPoint(-it->x, it->y)+m_Pos;
        appendFillCirclePoint(pVertexArray, curPt, minPt, maxPt, color, curVertex);
    }
}

void CircleNode::appendCirclePoint(VertexArrayPtr& pVertexArray, const DPoint& iPt, 
        const DPoint& oPt, Pixel32 color, int& i, int& curVertex)
{
    i++;
    double ratio = (double(i)/getNumCircumferencePoints());
    double curTC = (1-ratio)*m_TC1+ratio*m_TC2;
    pVertexArray->appendPos(oPt+m_Pos, DPoint(curTC, 0), color);
    pVertexArray->appendPos(iPt+m_Pos, DPoint(curTC, 1), color);
    pVertexArray->appendQuadIndexes(curVertex+1, curVertex, curVertex+3, curVertex+2); 
    curVertex += 2;
}

void CircleNode::appendFillCirclePoint(VertexArrayPtr& pVertexArray, const DPoint& curPt, 
        const DPoint& minPt, const DPoint& maxPt, Pixel32 color, int& curVertex)
{
    DPoint curTexCoord = calcFillTexCoord(curPt, minPt, maxPt);
    pVertexArray->appendPos(curPt, curTexCoord, color);
    pVertexArray->appendTriIndexes(0, curVertex, curVertex+1);
    curVertex++;
}

int CircleNode::getNumCircumferencePoints()
{
    return int(ceil((m_Radius*3)/8)*8);
}

void CircleNode::getEigthCirclePoints(vector<DPoint>& pts, double radius)
{
    int numPts = getNumCircumferencePoints();
    for (int i = 0; i <= numPts/8; ++i) {
        double ratio = (double(i)/numPts);
        double angle = ratio*2*3.14159;
        pts.push_back(getCirclePt(angle, radius));
    }
}

DPoint CircleNode::getCirclePt(double angle, double radius)
{
    return DPoint(sin(angle)*radius, -cos(angle)*radius);
}

}
