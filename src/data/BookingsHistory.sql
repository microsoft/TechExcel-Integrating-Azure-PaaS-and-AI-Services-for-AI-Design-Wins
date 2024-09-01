-- Run against the ContosoSuitesBookings database.

IF OBJECT_ID('dbo.Customer') IS NULL
BEGIN
	CREATE TABLE dbo.Customer
	(
		CustomerID INT NOT NULL CONSTRAINT [PK_Customer] PRIMARY KEY CLUSTERED,
		FirstName NVARCHAR(75) NOT NULL,
		LastName NVARCHAR(75) NOT NULL,
		MembershipBeginYear INT NOT NULL
	);

END
GO

IF OBJECT_ID('dbo.Hotel') IS NULL
BEGIN
	CREATE TABLE dbo.Hotel
	(
		HotelID INT NOT NULL CONSTRAINT [PK_Hotel] PRIMARY KEY CLUSTERED,
		HotelName NVARCHAR(150) NOT NULL,
		City NVARCHAR(75) NOT NULL,
		Country NVARCHAR(75) NOT NULL
	);
END
GO

IF OBJECT_ID('dbo.HotelRoomType') IS NULL
BEGIN
	CREATE TABLE dbo.HotelRoomType
	(
		HotelRoomTypeID INT NOT NULL CONSTRAINT [PK_HotelRoomType] PRIMARY KEY CLUSTERED,
		BedSize NVARCHAR(20) NOT NULL,
		NumberOfRooms INT NOT NULL,
		NumberOfBathrooms INT NOT NULL,
		HasKitchenette BIT NOT NULL
	);
END
GO

IF OBJECT_ID('dbo.HotelRoom') IS NULL
BEGIN
	CREATE TABLE dbo.HotelRoom
	(
		HotelRoomID INT NOT NULL CONSTRAINT [PK_HotelRoom] PRIMARY KEY CLUSTERED,
		HotelID INT NOT NULL,
		RoomNumber NVARCHAR(6) NOT NULL,
		HotelRoomTypeID INT NOT NULL,
		CONSTRAINT [FK_HotelRoom_Hotel] FOREIGN KEY(HotelID) REFERENCES dbo.Hotel(HotelID),
		CONSTRAINT [FK_HotelRoom_HotelRoomType] FOREIGN KEY(HotelRoomTypeID) REFERENCES dbo.HotelRoomType(HotelRoomTypeID)
	);
END
GO

IF OBJECT_ID('dbo.Booking') IS NULL
BEGIN
	CREATE TABLE dbo.Booking
	(
		BookingID INT NOT NULL CONSTRAINT [PK_Booking] PRIMARY KEY CLUSTERED,
		CustomerID INT NOT NULL,
		HotelID INT NOT NULL,
		StayBeginDate DATE NOT NULL,
		StayEndDate DATE NOT NULL,
		NumberOfGuests INT NOT NULL,
		CONSTRAINT [FK_Booking_Customer] FOREIGN KEY(CustomerID) REFERENCES dbo.Customer(CustomerID),
		CONSTRAINT [FK_Booking_Hotel] FOREIGN KEY(HotelID) REFERENCES dbo.Hotel(HotelID),
		CONSTRAINT [CK_Booking_Dates] CHECK(StayBeginDate < StayEndDate)
	);
END
GO

IF OBJECT_ID('dbo.BookingHotelRoom') IS NULL
BEGIN
	CREATE TABLE dbo.BookingHotelRoom
	(
		BookingHotelRoomID INT NOT NULL CONSTRAINT [PK_BookingHotelRoom] PRIMARY KEY CLUSTERED,
		BookingID INT NOT NULL,
		HotelRoomID INT NOT NULL,
		CONSTRAINT [FK_BookingHotelRoom_Booking] FOREIGN KEY(BookingID) REFERENCES dbo.Booking(BookingID),
		CONSTRAINT [FK_BookingHotelRoom_HotelRoom] FOREIGN KEY(HotelRoomID) REFERENCES dbo.HotelRoom(HotelRoomID)
	);
END
GO
IF NOT EXISTS
(
	SELECT 1
	FROM dbo.Customer
)
BEGIN
	INSERT INTO dbo.Customer
	(
		CustomerID,
		FirstName,
		LastName,
		MembershipBeginYear
	)
	VALUES
	(1, 'Amber', 'Rodriguez', 2013),
	(2, 'Ana', 'Bowman', 2013),
	(3, 'Dakota', 'Sanchez', 2000),
	(4, 'Amari', 'Rivera', 1992),
	(5, 'Briana', 'Hernandez', 1993);
END
GO
IF NOT EXISTS
(
	SELECT 1
	FROM dbo.Hotel
)
BEGIN
	INSERT INTO dbo.Hotel
	(
		HotelID,
		HotelName,
		City,
		Country
	)
	VALUES
	(1, 'Oceanview Inn', 'Noord', 'Aruba'),
	(2, 'Metro Business Hotel', 'Ponce', 'Puerto Rico'),
	(3, 'Grand Regency', 'San Juan', 'Puerto Rico'),
	(4, 'Beautiful Inn', 'Virgin Gorda', 'Virgin Islands');
END
GO
IF NOT EXISTS
(
	SELECT 1
	FROM dbo.HotelRoomType
)
BEGIN
	INSERT INTO dbo.HotelRoomType
	(
		HotelRoomTypeID,
		BedSize,
		NumberOfRooms,
		NumberOfBathrooms,
		HasKitchenette
	)
	VALUES
	(1, 'Queen', 1, 1, 0),
	(2, 'King', 1, 1, 0),
	(3, 'Double', 1, 1, 0),
	(4, 'King', 3, 1, 1),
	(5, 'King', 3, 2, 1);
END
GO
IF NOT EXISTS
(
	SELECT 1
	FROM dbo.HotelRoom
)
BEGIN
	INSERT INTO dbo.HotelRoom
	(
		HotelRoomID,
		HotelID,
		RoomNumber,
		HotelRoomTypeID
	)
	VALUES
	(1, 1, '105', 1),
	(2, 1, '107', 2),
	(3, 1, '215', 2),
	(4, 1, '203', 3),
	(5, 1, '305', 4),
	(6, 1, '405', 4),
	(7, 2, '201A', 1),
	(8, 2, '201B', 2),
	(9, 2, '101D', 2),
	(10, 2, '301A', 3),
	(11, 2, '301C', 4),
	(12, 2, '301D', 5),
	(13, 3, '129', 1),
	(14, 3, '121', 2),
	(15, 3, '118', 2),
	(16, 3, '106', 3),
	(17, 3, '102', 4),
	(18, 3, '101', 4),
	(19, 4, '315', 1),
	(20, 4, '316', 2),
	(21, 4, '317', 2),
	(22, 4, '318', 1),
	(23, 4, '319', 2),
	(24, 4, '320', 2);
END
GO
IF NOT EXISTS
(
	SELECT 1
	FROM dbo.Booking
)
BEGIN
	INSERT INTO dbo.Booking
	(
		BookingID,
		CustomerID,
		HotelID,
		StayBeginDate,
		StayEndDate,
		NumberOfGuests
	)
	VALUES
	(1, 3, 2, '2019-01-06', '2019-01-14', 2),
	(2, 2, 2, '2019-01-19', '2019-01-27', 1),
	(3, 3, 4, '2019-03-16', '2019-04-01', 2),
	(4, 1, 1, '2023-02-09', '2023-02-13', 1),
	(5, 4, 3, '2023-03-11', '2023-03-18', 1),
	(6, 1, 4, '2023-05-09', '2023-05-16', 3),
	(7, 5, 1, '2023-07-02', '2023-07-14', 4),
	(8, 3, 3, '2023-08-23', '2023-09-01', 1),
	(9, 5, 1, '2023-09-04', '2023-09-09', 2),
	(10, 2, 1, '2024-09-06', '2024-09-12', 1),
	(11, 3, 4, '2024-10-06', '2024-10-09', 2),
	(12, 4, 4, '2024-10-06', '2024-10-13', 3),
	(13, 1, 4, '2025-11-15', '2025-11-28', 2),
	(14, 5, 3, '2025-11-06', '2025-11-10', 4),
	(15, 1, 3, '2025-12-29', '2026-01-03', 2);
END
GO
IF NOT EXISTS
(
	SELECT 1
	FROM dbo.BookingHotelRoom
)
BEGIN
	INSERT INTO dbo.BookingHotelRoom
	(
		BookingHotelRoomID,
		BookingID,
		HotelRoomID
	)
	VALUES
	(1, 1, 9),
	(2, 2, 8),
	(3, 3, 20),
	(4, 3, 21),
	(5, 4, 6),
	(6, 5, 13),
	(7, 6, 23),
	(8, 6, 24),
	(9, 7, 1),
	(10, 7, 2),
	(11, 7, 4),
	(12, 8, 14),
	(13, 9, 5),
	(14, 10, 6);
END
GO
