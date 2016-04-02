/***************************************************************************
  plugin.cpp
  Plugin to draw scale bar on map
Functions:

-------------------
begin                : Jun 1, 2004
copyright            : (C) 2004 by Peter Brewer
email                : sbr00pwb@users.sourceforge.net

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
#ifndef QGSCALEBARPLUGIN
#define QGSCALEBARPLUGIN

#include "qgis.h"
#include "qgsdecorationitem.h"

class QPainter;

#include <QColor>

class APP_EXPORT QgsDecorationScaleBar: public QgsDecorationItem
{
    Q_OBJECT
  public:
    //! Constructor
    QgsDecorationScaleBar( QObject* parent = nullptr );
    //! Destructor
    virtual ~ QgsDecorationScaleBar();

  public slots:
    //! set values on the gui when a project is read or the gui first loaded
    void projectRead() override;
    //! save values to the project
    void saveToProject() override;

    //! this does the meaty bit of the work
    void render( QPainter * ) override;
    //! Show the dialog box
    void run() override;

  private:

    //! The size preferred size of the scale bar
    int mPreferredSize;
    //! Should we snap to integer times power of 10?
    bool mSnapping;
    //! Style of scale bar. An index and the translated text
    int mStyleIndex;
    QStringList mStyleLabels;
    //! The scale bar color
    QColor mColor;
    //! Margin percentage values
    int mMarginHorizontal;
    int mMarginVertical;

    friend class QgsDecorationScaleBarDialog;
};

#endif
