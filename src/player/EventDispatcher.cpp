//
//  libavg - Media Playback Engine. 
//  Copyright (C) 2003-2008 Ulrich von Zadow
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

#include "EventDispatcher.h"
#include "Event.h"

#include <string>

using namespace std;

namespace avg {

EventDispatcher::EventDispatcher()
{
}

EventDispatcher::~EventDispatcher() 
{
}

void EventDispatcher::dispatch() 
{
    vector<EventPtr> events;

    for (unsigned int i = 0; i < m_InputDevices.size(); ++i) {
        IInputDevicePtr pCurInputDevice = m_InputDevices[i];

        vector<EventPtr> curEvents = pCurInputDevice->pollEvents();
        vector<EventPtr>::iterator eventIt = curEvents.begin();
        events.insert(events.end(), curEvents.begin(), curEvents.end());

        for ( ; eventIt != curEvents.end(); eventIt++) {
            (*eventIt)->setInputDevice(pCurInputDevice);
        }
    }

    vector<EventPtr>::iterator it;
    for (it = events.begin(); it != events.end(); ++it) {
        handleEvent(*it);
    }
}

void EventDispatcher::addInputDevice(IInputDevicePtr pInputDevice)
{
    m_InputDevices.push_back(pInputDevice);
}

void EventDispatcher::addSink(IEventSink * pSink)
{
    m_EventSinks.push_back(pSink);
}

void EventDispatcher::sendEvent(EventPtr pEvent)
{
    handleEvent(pEvent);
}

void EventDispatcher::handleEvent(EventPtr pEvent)
{
    for (unsigned int i = 0; i < m_EventSinks.size(); ++i) {
        if (m_EventSinks[i]->handleEvent(pEvent)) {
            break;
        }
    }
}

}

